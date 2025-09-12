# Enable forward references in type hints (allows using types
# before they are defined in the code).
from __future__ import annotations

# ------------------------
# FastAPI Imports
# ------------------------

# FastAPI → main class to create the web application.
from fastapi import FastAPI

# Import your API routers (auth and users).
# These are defined in app/api/routes/auth.py and users.py.
from app.api.routes import auth, users


# ------------------------
# Application Setup
# ------------------------

# Create the FastAPI application instance.
# - `title` appears in auto-generated docs (Swagger UI / ReDoc).
app = FastAPI(title="Blog API")

# Include the auth routes under /api/v1/auth/*
app.include_router(auth.router, prefix="/api/v1")

# Include the user management routes under /api/v1/users/*
app.include_router(users.router, prefix="/api/v1")


# ------------------------
# Root & Health Endpoints
# ------------------------

# Simple root endpoint for sanity check.
# GET http://localhost:8000/
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Blog API!"}


# Health check endpoint for monitoring tools or Docker healthchecks.
# GET http://localhost:8000/healthz
@app.get("/healthz")
async def health():
    return {"status": "ok"}
