# Micro Blog API

This is a small FastAPI example that stays easy to follow but still includes auth:

- Create users
- Log in with email and password
- Use a bearer token to create posts
- Read one user or list users
- List posts

The code is split into a few small files:

- `main.py` defines the API routes.
- `db/models.py` defines the database tables.
- `db/schemas.py` defines request and response shapes.
- `db/crud.py` contains the database and auth operations.
- `db/database.py` creates the database connection.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
uvicorn main:app --reload
```

Open the docs at `http://127.0.0.1:8000/docs`.

For local development, the app uses `blog.db` if `DATABASE_URL` is not set.

## Endpoints

- `POST /users/`
- `POST /auth/login`
- `GET /users/`
- `GET /users/{user_id}`
- `POST /users/{user_id}/posts`
- `GET /posts`

## Notes

- The app uses `DATABASE_URL` when provided, which makes it ready for PostgreSQL on Render.
- If `DATABASE_URL` is not set, it falls back to local SQLite in `blog.db`.
- Passwords are hashed before storing them.
- Login returns an expiring JWT bearer token.
- Tests use a separate temporary database.

## Render Deployment

For Render, create a PostgreSQL database and set these environment variables on the web service:

- `DATABASE_URL`
- `SECRET_KEY`

Use this start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```
