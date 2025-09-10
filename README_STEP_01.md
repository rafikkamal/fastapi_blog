# FastAPI Blog — Step 1 (Bootstrap + Alembic + First Migration)

A minimal, async-ready FastAPI backend scaffold with:

* **FastAPI + Uvicorn** for API development
* **PostgreSQL** for reliable data persistence
* **SQLAlchemy (async)** as ORM
* **Alembic** for database migrations
* **Pydantic v2** with `pydantic-settings` for configuration
* **Dockerized setup** for local development

---

## ✨ Features

* **FastAPI & Uvicorn** – High-performance, async-ready web framework for building APIs.  
* **PostgreSQL** – Reliable and powerful relational database managed by Docker.  
* **SQLAlchemy (async)** – Object-Relational Mapper (ORM) with full async support.  
* **Alembic** – Lightweight database migration tool for managing schema changes.  
* **Pydantic v2** – Data validation and settings management via `pydantic-settings`.  
* **Dockerized Setup** – Easy local development with isolated services.  
* **Initial Migration** – Users table created and version-controlled with Alembic.  

---

## 📂 Project Structure

fastapi_blog/
├── .env                  # Environment variables
├── .dockerignore         # Docker ignore file
├── alembic/              # Alembic migrations directory
│   ├── versions/         # Generated migration files
│   ├── env.py            # Alembic runtime config
│   └── script.py.mako    # Migration template
├── app/                  # FastAPI application
│   ├── api/              # API routers (v1/)
│   ├── core/
│   │   ├── config.py     # App settings
│   │   └── database.py   # DB engine and session
│   ├── models/
│   │   ├── base.py       # Imports all models for Alembic
│   │   └── user.py       # User model
│   ├── schemas/          # Pydantic schemas (added later)
│   ├── init.py       # Makes 'app' a Python package
│   └── main.py           # FastAPI app entry point
├── docker-compose.yml    # Defines app and database services
├── Dockerfile            # Specifies the application's environment
├── requirements.txt      # Python dependencies
└── README.md             # This guide


---

## ⚙️ Requirements

* Docker & Docker Compose installed  
* Port **8000** (API) and **5432** (Postgres) must be free  

---

## 🚀 Quick Start

### 1️⃣ Create `.env`

```env
DATABASE_URL=postgresql+asyncpg://blog_user:blog_pass@db:5432/blog_db

# JWT bits (used in step 2; safe to add now)
JWT_SECRET_KEY=please_change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Optional bootstrap super admin (used in step 2)
SUPERADMIN_EMAIL=admin@example.com
SUPERADMIN_PASSWORD=Admin#Pass123
```

---

## 🐳 Build Containers

```
docker compose build
```

---

## 🚀 Run Services

```
docker compose up
```
---

Database Migrations (Alembic)
1. Generate Initial Migration (Users Table)

⚠️ Make sure you are in the project root, not inside the alembic/ folder.
```
docker compose run --rm -e PYTHONPATH=/code app alembic revision --autogenerate -m "init"
```

2. Apply the Migration
```
docker compose run --rm -e PYTHONPATH=/code app alembic upgrade head
```

✅ Verification Checklist
1. Containers Running
```
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```


You should see:

blog_api (FastAPI app)

blog_db (Postgres database)

2. API Reachable
```
curl http://localhost:8000/
```


Expected response:

`{"message": "Welcome to FastAPI Blog API!"}`

3. Alembic Version Applied
```
docker compose run --rm -e PYTHONPATH=/code app alembic current
docker compose run --rm -e PYTHONPATH=/code app alembic history | tail -n 5
```


You should see the init revision hash listed.

4. Database Tables Exist
```
docker compose exec db psql -U blog_user -d blog_db -c "\dt"
docker compose exec db psql -U blog_user -d blog_db -c "SELECT * FROM alembic_version;"
```


users table should appear.

alembic_version should contain the applied revision hash.

⚠️ Common Pitfalls & Fixes

ModuleNotFoundError: No module named 'app'
→ Ensure app/__init__.py exists.
→ Run Alembic with PYTHONPATH=/code.

Running from wrong folder
→ Always run docker compose ... from project root, not inside alembic/.

Pydantic v2 change (BaseSettings moved)
→ Install pydantic-settings.
→ Import with:

from pydantic_settings import BaseSettings


Alembic script.py.mako missing
→ Create alembic/script.py.mako manually.
→ Ensure alembic/versions/ exists:

mkdir -p alembic/versions


Async env.py not awaited
→ End alembic/env.py with:

asyncio.run(run_migrations_online())


Alembic logging KeyError: 'formatters'
→ Add logging sections in alembic.ini for loggers, handlers, and formatters.

Docker Compose warning: version key obsolete
→ Remove the version: line from docker-compose.yml.

Dockerfile parse errors (comments)
→ Place comments on separate lines, not after instructions.
