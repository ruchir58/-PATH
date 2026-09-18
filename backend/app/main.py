from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
import os

# Import models so Base metadata is populated
import app.models.models

# Create DB tables
Base.metadata.create_all(bind=engine)

# Create data directories if they don't exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/cleaned", exist_ok=True)
os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)

app = FastAPI(
    title="प्रगति-PATH API",
    description="API for the Student Academic Risk Early Warning System",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. Change in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to प्रगति-PATH API"}

from app.api.datasets import router as datasets_router
from app.api.ml import router as ml_router
from app.api.students import router as students_router
from app.api.analytics import router as analytics_router
from app.api.exports import router as exports_router

app.include_router(datasets_router, prefix="/datasets", tags=["datasets"])
app.include_router(ml_router, prefix="/datasets", tags=["ml"])
app.include_router(students_router, prefix="/datasets/{dataset_id}/students", tags=["students"])
app.include_router(analytics_router, prefix="/datasets", tags=["analytics"])
app.include_router(exports_router, prefix="/datasets", tags=["exports"])
