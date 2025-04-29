### Reflection on Learnings and Project Experience

Over the duration of this course, I have gained significant hands-on experience in designing, building, testing, and deploying real-world software applications. Through lectures, assignments, and this final project, I have deepened my understanding of full-cycle development practices including backend development with FastAPI, database interaction with SQLAlchemy, authentication and authorization using JWTs, and advanced testing methodologies with Pytest and HTTPX.

Working on the final project was both challenging and rewarding. I faced several technical hurdles such as resolving circular imports in modular Python applications, configuring asynchronous database interactions, and ensuring the CI/CD pipeline was stable. Each challenge became an opportunity to dive deeper into debugging, reading documentation, and improving my problem-solving skills.

I also learned the importance of containerization with Docker and the value of using automated pipelines (GitHub Actions) to catch bugs early and maintain code quality. Deploying the application to DockerHub taught me the significance of proper authentication, tagging images correctly, and making sure the application builds in different environments consistently.

Finally, I understood the importance of issue tracking, branching strategies, commit discipline, and QA testing as part of a professional development workflow — vital skills for any software engineer.

### Links to Project Work

## 5 QA Issues (Closed):

[QA Issue #1](https://github.com/mb2362/user_management_by_monil-baxi/tree/6-bug-refactor-authentication-and-minio-client-integration)

[QA Issue #2](https://github.com/mb2362/user_management_by_monil-baxi/tree/8-fix-typeerror-username-is-an-invalid-keyword-argument-for-user-in-test_user_profile_picpy)

[QA Issue #3](https://github.com/mb2362/user_management_by_monil-baxi/tree/10-fix-jwt-token-creation-and-decoding-issue)

[QA Issue #4](https://github.com/mb2362/user_management_by_monil-baxi/tree/12-fix-user-role-assignment-during-user-creation)

[QA Issue #5](https://github.com/mb2362/user_management_by_monil-baxi/tree/14-fix-error-handling-and-file-upload-for-profile-picture---minio-integration)

[QA Issue #6](https://github.com/mb2362/user_management_by_monil-baxi/tree/16-bug-missing-service-configuration-and-networking-issues)

## 10 New Test Cases:

```sh

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


```

## Feature Implementation:

Feature branch : https://github.com/mb2362/user_management_by_monil-baxi/tree/feature

## DockerHub Deployment

DockerHub Repository Link:
https://hub.docker.com/layers/monilbaxi/final-term/latest/images/sha256:fae0492b00f830eec18a7c17494289e11c5ed62a8569a0bd9bff73c12977d940?tab=layers

The project has been successfully containerized and pushed to DockerHub. The latest stable image is publicly available and ready to deploy in any containerized environment.

---
📂 Project Structure
# Project Structure

This document provides an overview of the project's directory structure and key files.

## Root Directory

```
FINAL-TERM [WSL: UBUNTU]
├── .github/                     # GitHub related files (e.g., workflows, issue templates)
├── .pytest_cache/               # Pytest cache directory
├── alembic/                     # Database migration scripts
├── app/                         # Main application code
│   ├── _pycache_/               # Python bytecode cache
│   ├── core/                    # Core application functionality
│   ├── models/                  # Database models
│   ├── routers/                 # API route definitions
│   ├── schemas/                 # Pydantic schemas for data validation
│   ├── services/                # Business logic services
│   ├── utils/                   # Utility functions and helpers
│   ├── __init__.py              # Package initializer
│   ├── database.py              # Database connection and session management
│   ├── dependencies.py          # Dependency injection definitions
│   └── main.py                  # Application entry point
├── email_templates/             # Email template files
├── nginx/                       # Nginx configuration files
├── settings/                    # Application settings and configurations
├── tests/                       # Test files
├── venv/                        # Python virtual environment
├── .dockerignore                # Files to exclude from Docker builds
├── .env                         # Environment variables (not in version control)
├── .env.sample                  # Sample environment variables template
├── .gitignore                   # Git ignore patterns
├── about.md                     # Project description and about information
├── alembic.ini                  # Alembic configuration file
├── docker-compose.yml           # Docker Compose configuration
├── docker.md                    # Docker usage documentation
├── Dockerfile                   # Docker container definition
├── features.md                  # Feature documentation
├── finalproject.md              # Final project documentation
├── git.md                       # Git workflow documentation
├── license.txt                  # Project license
├── logging.conf                 # Logging configuration
├── project_agile_req.md         # Agile requirements documentation
├── project_structure.txt        # Plain text version of project structure
├── pytest.ini                   # Pytest configuration
├── readme.md                    # Main project documentation
└── requirements.txt             # Python dependencies
```
---

✨ Author

Developed by mb2362