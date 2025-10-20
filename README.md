# FastAPI Auth Service

[🇷🇺 Читать на русском](./README.ru.md) 

## 🚀 Launch Instructions

1. Copy `.env.example` and rename it to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Build the Docker image and start the containers:
   ```bash
   docker build --tag fastapi:latest .
   docker compose up
   ```

The app will be available at:  
`http://localhost:8000`

---

## 🧩 Core Technologies

- **FastAPI** — web framework for REST APIs  
- **PostgreSQL** — main database  
- **SQLAlchemy** — ORM for database interactions  
- **Alembic** — schema migrations  
- **bcrypt** — JWT token creation and validation  
- **Docker / Docker Compose** — containerization and orchestration

---

## 🏗️ Application Architecture

The app implements authentication with JWT tokens managed by a session-based model:

- **Login:** on successful authentication, a `session_uuid` is generated and linked to access and refresh tokens. Tokens are stored in cookies.  
- **Refresh:** when the access token expires, the refresh token is used to issue a new one.  
- **Logout:** terminates the current session and invalidates all linked tokens.  
- **Abort sessions:** allows ending all active user sessions.  
- **View sessions:** users can list all active sessions with their IPs and timestamps.

---

## ⚙️ Session System Overview

1. A unique session UUID is generated at login.  
2. The UUID is stored in the database and linked to issued tokens.  
3. On requests, tokens are validated against an active session.  
4. When a user performs logout or abort, the session and all associated tokens are invalidated.  
5. Sessions can be viewed via the API.

---

## 📂 Containerization

- `Dockerfile` — FastAPI service build  
- `docker-compose.yml` — orchestration (FastAPI + PostgreSQL)
