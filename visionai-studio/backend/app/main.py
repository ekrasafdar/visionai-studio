from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import auth, predict, history, models_router, dashboard, profile, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VisionAI Studio API",
    description="Backend for the VisionAI Studio image classification platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(history.router)
app.include_router(models_router.router)
app.include_router(dashboard.router)
app.include_router(profile.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "VisionAI Studio API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
