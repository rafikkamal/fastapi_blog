from __future__ import annotations

from fastapi import FastAPI
from app.api.routes import auth, users

app = FastAPI(title="Blog API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

# Simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Blog API!"}

@app.get("/healthz")
async def health():
    return {"status": "ok"}
