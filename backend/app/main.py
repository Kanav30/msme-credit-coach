import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import owner, auth, cibil

app = FastAPI(
    title="MSME Credit Score Improvement Coach API",
    version="2.0.0",
    description="Credit score diagnostic, tailored improvement tips, daily habit logs, and trajectory simulator API for MSMEs.",
)

# Configure CORS for local development and deployed frontend origins (Vercel, Render)
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
env_origins = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [orig.strip() for orig in env_origins.split(",") if orig.strip()]
for default_orig in DEFAULT_ORIGINS:
    if default_orig not in allowed_origins:
        allowed_origins.append(default_orig)

# Dynamic regex matching Vercel deployments (*.vercel.app), Render (*.onrender.com), and localhost ports
# Allows any preview branch/subdomain on Vercel and Render while safely constraining to those domains
default_origin_regex = (
    r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$|"
    r"^https://.*\.vercel\.app$|"
    r"^https://.*\.onrender\.com$"
)
allow_origin_regex = os.getenv("ALLOWED_ORIGIN_REGEX", default_origin_regex)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=allow_origin_regex,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Mount endpoints at root
app.include_router(auth.router)
app.include_router(cibil.router)
app.include_router(owner.router)

# Also mount under /api prefix for proxy-less and transparent API routing
app.include_router(auth.router, prefix="/api")
app.include_router(cibil.router, prefix="/api")
app.include_router(owner.router, prefix="/api")


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
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
