from fastapi import FastAPI
from app.api.routes import downloads, health_check, training, jobs
from fastapi.middleware.cors import CORSMiddleware
from app.services.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="Transpetro MLOps API",
    version="1.0.0",
    description="API da primeira release da plataforma de treinamentos YOLO.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check.router)
app.include_router(training.router)
app.include_router(jobs.router)
app.include_router(downloads.router)
