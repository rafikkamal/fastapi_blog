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



---

### 🔧 Environment Variables

Add to your `.env`:

```env
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

`docker compose exec app alembic revision --autogenerate -m "auth user"`

Apply them:

`docker compose exec app alembic upgrade head`

---

### ▶️ Run Services
`docker compose up -d`

---

### ▶️ Health check
`curl http://localhost:8000/healthz`

```
{"status":"ok"}
```

---

### ⚠️ Common Pitfalls

401 Unauthorized → missing/expired Bearer token

403 Forbidden → insufficient role

Password strength error → must include uppercase, lowercase, digit, and symbol

Enum migration issues → always give your Postgres enums a name

Credential mismatch → .env DATABASE_URL must match POSTGRES_* in docker-compose.yml
