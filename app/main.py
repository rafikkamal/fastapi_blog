from fastapi import FastAPI

# Create FastAPI app instance
app = FastAPI(title="FastAPI Blog")

# Simple root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Blog API!"}
