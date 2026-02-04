# Bump commit: 2026-02-04
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import analysis
import os
from contextlib import asynccontextmanager
from init_db import init_models

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_models()
    yield

app = FastAPI(title="Riot Win Prediction API", lifespan=lifespan)

# CORS setup
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
