## 🚀 Step 2: Authentication & Authorization

We added **user authentication with OAuth2 + JWT** and **role-based authorization**.

---

### ✨ Features

* **JWT-based OAuth2** with Bearer tokens
* **User registration** (`/api/v1/auth/register`) → creates a `subscriber`
* **Login** (`/api/v1/auth/login`) → returns JWT token
* **Current user** (`/api/v1/auth/me`)
* **Role-based guards** with `super_admin`, `editor`, `subscriber`
* Example **admin-only** endpoints under `/api/v1/users`

---

### 📂 Project Structure (new/updated)

```
app/
├── api/
│   ├── deps.py
│   └── routes/
│       ├── auth.py
│       └── users.py
├── core/
│   ├── security.py
│   └── settings.py       # extended with JWT_* values
├── crud/
│   └── crud_user.py
├── models/
│   └── user.py
└── main.py               # includes auth & users routers
alembic/
├── versions/
│   └── 2024090801_create_users.py      # or your timestamp
```

---

### 🔧 Environment Variables

Add to your `.env`:

```
# Database (matches docker-compose.yml)
DATABASE_URL=postgresql+asyncpg://blog_user:blog_pass@db:5432/blog_db

# JWT
JWT_SECRET=please-change-to-a-long-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

### 🗃️ Database Migration

Generate migrations:

```
docker compose exec app alembic revision --autogenerate -m "auth user"
```

Apply them:

```
docker compose exec app alembic upgrade head
```

---

### ▶️ Run Services
```
docker compose up -d
```


Health check:

```
curl http://localhost:8000/healthz
```

`{"status":"ok"}`

---

### ⚠️ Common Pitfalls

* 401 Unauthorized → missing/expired Bearer token
* 403 Forbidden → insufficient role
* Password strength error → must include uppercase, lowercase, digit, and symbol
* Enum migration issues → always give your Postgres enums a name
* Credential mismatch → `.env` DATABASE_URL must match POSTGRES_* in docker-compose.yml

---

### 🌱 Seeding default users

Create three default users (idempotent: safe to run multiple times):

* **Super Admin** — `admin@example.com / password123`
* **Editor** — `editor@example.com / password123`
* **Subscriber** — `subscriber@example.com / password123`

Make sure you’ve run the database migrations first:

```
docker compose exec app alembic upgrade head
```

Run the seeder (module)
```
docker compose exec app python -m app.seeds.seed_users
```

Expected output (first run):

`Users created: 3, skipped (already existed): 0`

Subsequent runs:

`Users created: 0, skipped (already existed): 3`

### 🛠️ Management CLI

We provide a simple CLI to run seeding.

Seed via CLI
```
docker compose exec app python -m app.management.cli seed:users
```

---

### 🩹 Troubleshooting

* 401: Could not validate credentials → Missing/expired token, or wrong Authorization header format.
* 400: Incorrect email or password → Check credentials.
* 403: Insufficient permissions → You’re not logged in as super_admin.
* Import/module errors → Ensure `app/__init__.py`, `app/models/__init__.py`, `app/core/__init__.py` exist.
* Seeder bcrypt warning (“error reading bcrypt version”) → harmless; pin versions to silence: