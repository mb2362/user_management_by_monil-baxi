# ⚠️ Database Url is missing

## Common Issues

- **Missing `DATABASE_URL`**  
  Make sure your `.env` file exists and is correctly loaded.
  
- **Invalid Driver**  
  If you see errors like:
  
  > `The asyncio extension requires an async driver to be used.`

  Make sure your connection URL uses `asyncpg`, not `psycopg2`.

  Correct:
  ```
  postgresql+asyncpg://user:pass@host/dbname
  ```

  Incorrect:
  ```
  postgresql+psycopg2://user:pass@host/dbname
  ```

- **Database Not Running**  
  Ensure that PostgreSQL is running and accessible at the host and port you configured.

## 📚 Solution for DATABASE_URL Issue

If you encounter `Database Url is missing` or `The asyncio extension requires an async driver to be used` errors:

1. **Update the `.env` file**:

    Add the correct `DATABASE_URL` in the `.env` file.

    Example:
    ```env
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mydatabase
    ```

2. **Update Alembic's `env.py`**:

    Set the main option to use the environment variable:

    ```python
    config.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    ```

This ensures your application and Alembic both use the correct asynchronous database URL.


## ✨ Author

Developed by [mb2362](https://github.com/mb2362)

---
