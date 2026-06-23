from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import Base, engine
from app.models import models  # noqa: ensures models are registered
from app.api.routes import router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quantis API",
              description="AI-Powered Financial Digital Twin", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])
app.include_router(router)


@app.get("/")
def root():
    return {"service": "Quantis", "status": "ok", "docs": "/docs"}
