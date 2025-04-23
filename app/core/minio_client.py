from minio import Minio
from app.core.config import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME, MINIO_SECURE
)

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# Create bucket if it doesn't exist
if not client.bucket_exists(MINIO_BUCKET_NAME):
    client.make_bucket(MINIO_BUCKET_NAME)