from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import owner, auth, cibil

app = FastAPI(
    title="MSME Credit Score Improvement Coach API",
    version="2.0.0",
    description="Credit score diagnostic, tailored improvement tips, daily habit logs, and trajectory simulator API for MSMEs.",
)

# Enable CORS for frontend development and production access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cibil.router)
app.include_router(owner.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "msme-credit-score-coach",
        "version": "2.0.0",
        "endpoints": {
            "auth": "/auth",
            "cibil": "/cibil",
            "owner": "/owner",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
