from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
from http import client
import io
import secrets
from typing import Optional, Dict, List
from fastapi import UploadFile, HTTPException
from PIL import Image
from pydantic import ValidationError
from sqlalchemy import func, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import MINIO_BUCKET_NAME
from app.dependencies import get_settings, get_minio_client
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.crud_profile_picture import create_bucket_if_not_exists, delete_old_profile_picture
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from uuid import UUID, uuid4
from app.services.email_service import EmailService
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> Optional[User]:
        try:
            validated_data = UserCreate(**user_data).model_dump()
            existing_user = await cls.get_by_email(session, validated_data['email'])
            if existing_user:
                logger.error("User with given email already exists.")
                return None
            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            new_user = User(**validated_data)
            new_nickname = generate_nickname()
            while await cls.get_by_nickname(session, new_nickname):
                new_nickname = generate_nickname()
            new_user.nickname = new_nickname
            user_count = await cls.count(session)
            new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS            
            if new_user.role == UserRole.ADMIN:
                new_user.email_verified = True
            else:
                new_user.verification_token = generate_verification_token()
                await email_service.send_verification_email(new_user)

            session.add(new_user)
            await session.commit()
            return new_user
        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None
    
    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)
            if 'password' in validated_data:
                validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            query = update(User).where(User.id == user_id).values(**validated_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                session.refresh(updated_user)
                logger.info(f"User {user_id} updated successfully.")
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update attempt.")
            return None
        except Exception as e:
            logger.error(f"Error during user update: {e}")
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str], get_email_service) -> Optional[User]:
        return await cls.create(session, user_data, get_email_service)

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await cls.get_by_email(session, email)
        if user:
            if not user.email_verified or user.is_locked:
                return None
            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= settings.max_login_attempts:
                    user.is_locked = True
                session.add(user)
                await session.commit()
        return None

    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        user = await cls.get_by_email(session, email)
        return user.is_locked if user else False

    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0
            user.is_locked = False
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.verification_token == token:
            user.email_verified = True
            user.verification_token = None
            user.role = UserRole.AUTHENTICATED
            session.add(user)
            await session.commit()
            return True
        return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        return result.scalar()

    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0
            session.add(user)
            await session.commit()
            return True
        return False

    @staticmethod
    async def upload_profile_picture(user: User, db: AsyncSession, file: UploadFile, minio_client) -> User:
        """
        Upload and update the user's profile picture.
        """
        try:
            # Check if the file type is valid
            valid_file_types = ["image/jpeg", "image/png", "image/gif"]
            if file.content_type not in valid_file_types:
                raise HTTPException(status_code=400, detail="Invalid file format")

            # Check file size (limit to 5MB for example)
            if len(file.file.read()) > 5 * 1024 * 1024:
                raise HTTPException(status_code=400, detail="File is too large")

            # Move the file pointer back to the start
            file.file.seek(0)

            # Resize the image if necessary (use PIL)
            image = Image.open(file.file)
            image.thumbnail((200, 200))  # Resize image to fit profile picture size

            # Save image to MinIO
            bucket_name = MINIO_BUCKET_NAME
            create_bucket_if_not_exists(minio_client, bucket_name)

            file.filename = f"{secrets.token_hex(8)}_{file.filename}"
            minio_client.put_object(bucket_name, file.filename, file.file)

            # Delete old profile picture if exists
            # if user.profile_picture:
            #     delete_old_profile_picture(minio_client, bucket_name, user.profile_picture)

            # Update the user's profile picture URL in the database
            user.profile_picture_url = f"http://{minio_client.endpoint}/{bucket_name}/{file.filename}"

            db.add(user)
            await db.commit()
            await db.refresh(user)

            logger.info(f"Profile picture uploaded for user {user.username}")
            return user
        except HTTPException as e:
            raise e  # Reraise HTTP exceptions
        except Exception as e:
            logger.error(f"Error uploading profile picture: {e}")
            raise HTTPException(status_code=500, detail="Error uploading profile picture")