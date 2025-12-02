# Deployment Guide - Railway

This application is designed to be easily deployed to Railway.app with a PostgreSQL database.

## Prerequisites

- A GitHub account.
- A Railway account (login with GitHub).

## Steps

1.  **Push to GitHub**:
    - Commit your code and push it to a new GitHub repository.

2.  **Create Project on Railway**:
    - Go to [Railway Dashboard](https://railway.app/dashboard).
    - Click "New Project" -> "Deploy from GitHub repo".
    - Select your repository.

3.  **Add Database**:
    - In the project view, right-click (or click "New") -> "Database" -> "PostgreSQL".
    - This will add a Postgres service to your project.

4.  **Configure Variables**:
    - Click on the **FastAPI service** (your app).
    - Go to the "Variables" tab.
    - Add the following variables:
        - `DATABASE_URL`: `${{PostgreSQL.DATABASE_URL}}` (Railway usually auto-injects this, but ensure it's set).
        - `SECRET_KEY`: Generate a strong random string.
        - `DEBUG`: `False`

5.  **Build & Deploy**:
    - Railway will automatically detect the `requirements.txt` and `Procfile` (if present) or use `uvicorn` command.
    - If needed, set the **Start Command** in Settings to:
      ```bash
      uvicorn app.main:app --host 0.0.0.0 --port $PORT
      ```

6.  **Verify**:
    - Once deployed, open the provided URL.
    - Go to `/auth/setup` to initialize the database with the default shop and user (or run a migration script if you set one up).
    - Login and start using the app.

## Database Migrations

For production, it is recommended to use Alembic for migrations instead of `Base.metadata.create_all`.

1.  Initialize Alembic: `alembic init alembic`
2.  Configure `alembic.ini` and `env.py` to use `DATABASE_URL`.
3.  Generate migration: `alembic revision --autogenerate -m "Initial migration"`
4.  Apply migration: `alembic upgrade head`
