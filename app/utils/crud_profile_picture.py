import uuid
from fastapi import UploadFile, HTTPException
from app.core.minio_client import client
from app.core.config import MINIO_BUCKET_NAME
from minio.error import S3Error

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"]

async def validate_file_size(file: UploadFile) -> bytes:
    """Helper function to validate file size."""
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large. Max 10MB.")
    return contents

async def upload_profile_picture(file: UploadFile, old_file_path: str = None) -> str:
    """
    Upload profile picture to MinIO storage and return the file path.
    """
    # Validate file type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use JPEG or PNG.")

    # Validate file size
    contents = await validate_file_size(file)

    # Reset file pointer
    file.file.seek(0)

    # Ensure bucket exists
    try:
        if not client.bucket_exists(MINIO_BUCKET_NAME):
            client.make_bucket(MINIO_BUCKET_NAME)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Storage bucket does not exist. {str(e)}")

    # Generate new filename
    file_ext = file.filename.split(".")[-1]
    filename = f"profile-pics/{uuid.uuid4()}.{file_ext}"

    # Upload file to MinIO
    try:
        client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=filename,
            data=file.file,
            length=len(contents),
            content_type=file.content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not connect to MinIO server. {str(e)}")

    # Delete old profile picture if it exists
    if old_file_path:
        try:
            client.remove_object(MINIO_BUCKET_NAME, old_file_path)
        except Exception as e:
            # Handle potential errors silently
            pass  # You may want to log this silently

    return f"{MINIO_BUCKET_NAME}/{filename}"

async def create_bucket_if_not_exists(minio_client, bucket_name):
    return minio_client.create_bucket_if_not_exists(minio_client, bucket_name)

async def delete_old_profile_picture(user_id: str, old_file_path: str):
    """
    Delete old profile picture from MinIO.
    """
    try:
        client.remove_object(MINIO_BUCKET_NAME, old_file_path)
    except S3Error as err:
        raise Exception(f"❌ MinIO Error: {err}")
    except Exception as e:
        raise Exception(f"❌ Could not delete old profile picture from MinIO: {str(e)}")