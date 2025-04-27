from minio import Minio
from minio.error import S3Error
from app.core.config import (
    MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY,
    MINIO_BUCKET_NAME, MINIO_SECURE
)

# Initialize MinIO client
client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

# This function now takes `minio_client` and `bucket_name` as parameters
def create_bucket_if_not_exists(minio_client, bucket_name):
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully.")
        else:
            print(f"Bucket '{bucket_name}' already exists.")
    except S3Error as err:
        print(f"❌ MinIO Error: {err}")
    except Exception as e:
        print(f"❌ Could not connect to MinIO: {e}")


# Call the function to ensure the bucket exists
create_bucket_if_not_exists(client,MINIO_BUCKET_NAME)