# [Bug] : Refactor authentication and MinIO client integration #6

## Overview

This update focuses on improving the modularity, error handling, and structure of the FastAPI application, particularly in the areas of database session management, user authentication, and MinIO client integration.

---

## Changes Introduced

### 🚀 MinIO Client Integration
- Added a `get_minio_client` function to provide the MinIO client instance.
- MinIO client is now centrally managed via `app/core/minio_client.py` for better modularity and testability.

### 🚄️ Database Session Dependency
- Refactored the `get_db` function:
  - Now yields a database session from the session factory provided by the `Database` class.
  - Added exception handling to manage database session errors gracefully.

### 🔒 Authentication and Role Validation
- Updated `get_current_user` function:
  - Decodes and validates JWT tokens to fetch the user and role details securely.
- Refactored `require_role` dependency:
  - Ensures that a user’s role matches the required role for accessing specific endpoints.

### ⚙️ Environment Configuration
- Integrated `dotenv`:
  - Environment variables are now loaded from a `.env` file.
  - Improves deployment flexibility and security.

### 📦 Additional Imports
- Added necessary imports:
  - `UUID` for unique identifiers.
  - `Minio` for S3-compatible object storage operations.
  - `load_dotenv` for environment management.
  - Others to support new features and refactorings.

---

## How to Run

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up `.env` file**:
   - Create a `.env` file at the root.
   - Include necessary environment variables like:
     ```
     MINIO_ENDPOINT=localhost:9000
     MINIO_ACCESS_KEY=youraccesskey
     MINIO_SECRET_KEY=yoursecretkey
     SECRET_KEY=yourjwtsecret
     DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
     ```

3. **Start the application using Docker**:
   ```bash
   docker compose up --build
   ```

4. **API Documentation**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Folder Structure (Key Components)

```
app/
 ├── core/
 │    ├── config.py        # Environment variable loading
 │    └── minio_client.py   # MinIO client setup
 ├── utils/
 │    ├── dependencies.py      # get_db dependency
 ├── models/
 ├── schemas/
 ├── routers/
 └── main.py
.env
requirements.txt
Dockerfile
docker-compose.yml
```

---

## Notes
- Ensure your MinIO server is running locally or adjust `MINIO_ENDPOINT` in the `.env` accordingly.
- Properly configure roles and permissions for sensitive operations.
- Error handling has been strengthened but further specific exceptions can still be added for finer control.