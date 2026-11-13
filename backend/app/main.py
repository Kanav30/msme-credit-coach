import os
import logging
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import owner, auth, cibil

logger = logging.getLogger("msme_credit_coach")
logging.basicConfig(level=logging.INFO)

# Production Environment & Documentation Lock
is_production = os.getenv("APP_ENV", "development").lower() == "production"
enable_docs = os.getenv("ENABLE_DOCS", "false" if is_production else "true").lower() == "true"

app = FastAPI(
    title="MSME Credit Score Improvement Coach API",
    version="2.0.0",
    description="Credit score diagnostic, tailored improvement tips, daily habit logs, and trajectory simulator API for MSMEs.",
    debug=False,
    docs_url="/docs" if enable_docs else None,
    redoc_url="/redoc" if enable_docs else None,
    openapi_url="/openapi.json" if enable_docs else None,
)

# Global Security Response Headers Middleware (Enforce HTTPS, Frame Protection, MIME sniffing prevention)
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    # HSTS: Enforce HTTPS for 2 years (63072000 seconds) including subdomains
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    # Prevent browsers from MIME-sniffing away from declared Content-Type
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Prevent clickjacking / frame embedding
    response.headers["X-Frame-Options"] = "DENY"
    # Cross-site scripting (XSS) filter
    response.headers["X-XSS-Protection"] = "1; mode=block"
    # Referrer policy to prevent leaking URL parameters across domains
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Permissions policy restricting risky browser features
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # Mask server identification
    if "server" in response.headers:
        del response.headers["server"]
    return response


# Global Unhandled Exception Handler (Turn off raw error tracebacks in production)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled server exception on %s %s: %s", request.method, request.url.path, exc, exc_info=True)
    if is_production:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred. Please contact system support."},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"Internal Server Error: {str(exc)}"},
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
        },
    }


@app.get("/health")
@app.get("/api/health")
def health_check():
    return {"status": "healthy"}


@app.get("/admin")
@app.get("/api/admin")
def admin_portal(request: Request):
    """
    Administrative management and audit endpoint.
    Protected by ADMIN_SECRET_KEY / X-Admin-Key header.
    Unauthenticated public access is strictly locked (HTTP 403 Forbidden).
    """
    admin_secret = os.getenv("ADMIN_SECRET_KEY")
    provided_key = request.headers.get("X-Admin-Key") or request.headers.get("X-Admin-Secret")
    if not admin_secret or not provided_key or provided_key != admin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Administrative credentials required to access this endpoint.",
        )
    return {
        "status": "authenticated",
        "admin_access": True,
        "environment": os.getenv("APP_ENV", "development"),
        "database_engine": os.getenv("DB_ENGINE", "mysql"),
        "security_policy": "enforced",
    }
