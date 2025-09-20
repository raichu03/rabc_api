# Backend Permissions (RBAC) API

This module enforces role-based access control (RBAC) in a FastAPI backend so users can only perform actions allowed by their role. It authenticates users via OAuth2 Password flow, issues JWTs, and gates API endpoints with role checks.

Expected outcome: API endpoints that enforce permissions per role, with clear install/run steps and guidance for production hardening (data filtering, action validation, and authorization best practices).

## What data to feed

Provide environment and configuration, not a dataset:

- A `.env` file with secret settings (see Configuration)
- A `user.json` file with users and hashed passwords (sample included)
- Optional: connect to a real database and swap out the sample JSON user store

Requirements and constraints:
- Keep your `SECRET_KEY` secret (never commit real keys)
- Choose a robust JWT algorithm (HS256 by default)
- Store passwords hashed (bcrypt via Passlib)

## How it works

1. Authenticate and issue token
   - POST `/token` accepts `username` and `password` (form-encoded) and verifies against `user.json`.
   - On success, returns a JWT with `sub` (username) and `role` claims.
2. Authorize per endpoint
   - Each protected endpoint requires a Bearer token.
   - A reusable `has_permission([roles...])` dependency enforces allowed roles.
3. Enforce actions by role
   - Viewer can read only; Moderator can create; Admin can create and delete.

Error modes:
- 401 Unauthorized: missing/invalid token (decode error or wrong signature)
- 403 Forbidden: token valid but role lacks permission

## Module overview

Files:
- `main.py`
  - FastAPI app startup and `/token` for OAuth2 Password → JWT.
  - `/health` endpoint for basic liveness.
- `endpoints.py`
  - `get_current_user()` decodes JWT into `TokenData`.
  - `has_permission(required_roles)` dependency to enforce RBAC.
  - Sample endpoints under `/api`: `GET /data`, `POST /data`, `DELETE /data`.
- `models.py`
  - Pydantic models: `Token`, `TokenData`, `HealthCheckResponse`, `Data`.
- `utils.py`
  - Loads users from `user.json`, verifies bcrypt password, creates JWT.
- `user.json`
  - Sample users with bcrypt-hashed passwords and roles: `admin`, `moderator`, `viewer`.
- `.env`
  - App secrets such as `SECRET_KEY` and `ALGORITHM`.

## Quick start

Install dependencies (from repo root):

```bash
pip install -r requirements.txt
```

Run the API (from repo root):

```bash
# Option 1: run through Python entrypoint
python task-5/main.py

# Option 2: run through uvicorn directly
uvicorn task-5.main:app --host 0.0.0.0 --port 8000 --reload
```

## Configuration

- Location: `task-5/.env`
- Variables:

```
SECRET_KEY=<a_string_password>
ALGORITHM=HS256
```

Notes:
- Keep `SECRET_KEY` unpredictable and private.
- HS256 is adequate for many cases; consider rotating keys periodically.

Users and roles: `task-5/user.json`

```json
[
  {"username": "admin", "password": "<bcrypt_hash>", "role": "admin"},
  {"username": "moderator", "password": "<bcrypt_hash>", "role": "moderator"},
  {"username": "viewer", "password": "<bcrypt_hash>", "role": "viewer"}
]
```

To add a new user, generate a bcrypt hash:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("plain_password_here"))
```

## API and role matrix

Base URL: `http://localhost:8000`

- POST `/token` → returns `{ access_token, token_type }`
- GET `/health` → returns liveness info
- GET `/api/data` → roles: admin, moderator, viewer
- POST `/api/data` → roles: admin, moderator
- DELETE `/api/data` → roles: admin

Role matrix:

- viewer: read
- moderator: read, create
- admin: read, create, delete

HTTP statuses:
- 401 Unauthorized: invalid/missing token
- 403 Forbidden: role not permitted for action

## Use the interactive API docs (no code required)

You can test authentication and role-based permissions entirely through the built-in interactive docs.

Open: `http://localhost:8000/docs`

Steps:
1) Get a token
   - Expand `POST /token`.
   - Click “Try it out”.
   - Enter `username` and `password` for a user from `user.json` (e.g., username: `admin`, password: the plaintext corresponding to the stored bcrypt hash).
   - Execute to receive `{ "access_token": "...", "token_type": "bearer" }`.

2) Authorize
   - Click the “Authorize” button at the top right.
   - In the `value` field, paste the token in the format: `Bearer <access_token>`.
   - Click “Authorize”, then “Close”.

3) Call protected endpoints
   - Expand `GET /api/data` and click “Try it out” → Execute.
     - Expected for all roles (viewer/moderator/admin): 200 with a message indicating you can view the data.
   - Expand `POST /api/data` → “Try it out” → provide the request body field shown in the docs.
     - Expected for moderator/admin: 200 with a confirmation message.
     - Expected for viewer: 403 with detail indicating insufficient privileges.
   - Expand `DELETE /api/data` → “Try it out”.
     - Expected for admin: 200 with a deletion confirmation.
     - Expected for moderator/viewer: 403 with detail indicating insufficient privileges.

Common responses:
- 200 OK: the operation is allowed for the authenticated user’s role.
- 401 Unauthorized: token missing/invalid or expired.
- 403 Forbidden: token valid, but role not allowed to perform this action.