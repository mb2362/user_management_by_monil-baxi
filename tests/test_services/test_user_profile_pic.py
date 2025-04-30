from PIL import Image
import uuid
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.user_model import User, UserRole
from app.services.user_service import UserService
from io import BytesIO
from fastapi import HTTPException
from app.core.config import (MINIO_BUCKET_NAME)

@pytest.fixture
def db():
    # Create and return a mock database session with async methods
    mock_db = MagicMock()
    # Ensure the commit and refresh methods are async and return a value
    mock_db.commit = AsyncMock(return_value=None)  # Mock async commit
    mock_db.refresh = AsyncMock(return_value=None)  # Mock async refresh
    mock_db.add = MagicMock()  # Regular method call, not async
    mock_db.close = MagicMock()  # Regular method call, not async
    yield mock_db


@pytest.fixture
def minio_client_mock():
    # Create and return a mocked MinIO client with async methods
    mock_minio = MagicMock()
    # Simulate a successful object upload (you can update this with more specific behavior)
    mock_minio.put_object = MagicMock(return_value="http://mocked_endpoint/mock_bucket/profile.jpg")
    # Simulate delete operation (you can adjust for other scenarios)
    mock_minio.delete_object = MagicMock(return_value=None)
    # You can also add any other MinIO methods needed
    mock_minio.bucket_name = "mock_bucket"
    mock_minio.endpoint = "http://mocked_endpoint"
    yield mock_minio


@pytest.mark.asyncio
async def test_upload_profile_picture(db, minio_client_mock):
    user = User(
        id=uuid.uuid4(),
        nickname="TestNickname",
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Simulate a valid profile picture file (JPEG format)
    file = MagicMock()
    file.filename = "profile.jpg"
    file.content_type = "image/jpeg"
    file.file = BytesIO(b"valid image content")

    # Mock the bucket_exists method to simulate a bucket existing
    minio_client_mock.bucket_exists.return_value = False  # Simulating that the bucket doesn't exist

    with patch.object(Image, 'open', return_value=MagicMock(spec=Image.Image)) as mock_open:
        updated_user = await UserService.upload_profile_picture(user, db, file, minio_client_mock)

    # Verify the MinIO call to create the bucket
    minio_client_mock.make_bucket.assert_called_once_with(MINIO_BUCKET_NAME)


@pytest.mark.asyncio
async def test_upload_profile_picture(db, minio_client_mock):
    user = User(
        id=uuid.uuid4(),
        nickname="TestNickname",
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Simulate a valid profile picture file (JPEG format)
    file = MagicMock()
    file.filename = "profile.jpg"
    file.content_type = "image/jpeg"
    file.file = BytesIO(b"valid image content")

    with patch.object(Image, 'open', return_value=MagicMock(spec=Image.Image)) as mock_open:
        updated_user = await UserService.upload_profile_picture(user, db, file, minio_client_mock)
        # Further assertions can go here


@pytest.mark.asyncio
async def test_upload_profile_picture_invalid_format(db, minio_client_mock):
    user = User(
        id=uuid.uuid4(),
        nickname="TestNickname",
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN  # Set role to 'ADMIN'
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Simulate an invalid profile picture file (e.g., a non-image file)
    file = MagicMock()
    file.filename = "profile.txt"
    file.content_type = "text/plain"
    file.file = BytesIO(b"dummy text content")

    # Call the upload_profile_picture method and expect a 400 error (invalid file format)
    with pytest.raises(HTTPException, match="Invalid file format"):
        await UserService.upload_profile_picture(user, db, file, minio_client_mock)


@pytest.mark.asyncio
async def test_upload_profile_picture_large_file(db, minio_client_mock):
    user = User(
        id=uuid.uuid4(),
        nickname="TestNickname",
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN  # Set role to 'ADMIN'
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Simulate a large profile picture file (e.g., 10MB file)
    file = MagicMock()
    file.filename = "large_profile.jpg"
    file.content_type = "image/jpeg"
    file.file = BytesIO(b"dummy" * 10 * 1024 * 1024)  # 10MB content

    # Call the upload_profile_picture method and expect a 400 error (file too large)
    with pytest.raises(HTTPException, match="File is too large"):
        await UserService.upload_profile_picture(user, db, file, minio_client_mock)


@pytest.mark.asyncio
async def test_upload_profile_picture_minio_error(db, minio_client_mock):
    user = User(
        id=uuid.uuid4(),
        nickname="TestNickname",
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword",
        role=UserRole.ADMIN  # Set role to 'ADMIN'
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Simulate a profile picture file
    file = MagicMock()
    file.filename = "profile.jpg"
    file.content_type = "image/jpeg"
    file.file = BytesIO(b"dummy image content")

    # Simulate a MinIO error (e.g., connection issue)
    minio_client_mock.put_object = MagicMock(side_effect=Exception("MinIO connection failed"))

    # Call the upload_profile_picture method, expecting an exception due to MinIO error
    with pytest.raises(HTTPException, match="Error uploading profile picture"):
        await UserService.upload_profile_picture(user, db, file, minio_client_mock)


# @pytest.mark.asyncio
# async def test_delete_old_profile_picture(db, minio_client_mock):
#     user = User(
#         id=uuid.uuid4(),
#         nickname="TestNickname",
#         username="testuser",
#         email="testuser@example.com",
#         hashed_password="hashedpassword",
#         profile_picture="old_profile_picture.jpg",  # Existing profile picture
#         role=UserRole.ADMIN  # Set role to 'ADMIN'
#     )
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)

#     # Simulate deleting old profile picture from MinIO
#     await UserService.delete_old_profile_picture(user, minio_client_mock)

#     # Assertions to ensure the MinIO delete operation is called with correct arguments
#     minio_client_mock.delete_object.assert_called_once_with(
#         bucket_name=minio_client_mock.bucket_name, object_name=user.profile_picture
#     )
