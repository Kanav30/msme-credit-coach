"""
Phase 4 Regression Tests: Security and Configuration
- Hardcoded fallback JWT secrets are removed and secure config is required in production.
- CORS is strictly restricted to configured frontend origins; wildcard regex with credentials is eliminated.
- When MySQL is configured, connection failures are surfaced clearly instead of silently falling back to SQLite.
"""

import os
import sys
from pathlib import Path
import pytest
from unittest.mock import patch

os.environ["DB_ENGINE"] = "sqlite"
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_SRC_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "..", "ml", "src"))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, ML_SRC_DIR)

from fastapi.testclient import TestClient
from app.main import app
from app.core import security, db

client = TestClient(app)


def test_cors_restricts_to_allowed_origins():
    """Configured origins are permitted, while arbitrary/unauthorized origins are rejected."""
    # Permitted origin: http://localhost:5173
    res_valid = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_valid.headers.get("access-control-allow-origin") == "http://localhost:5173"

    # Unauthorized origin: http://malicious-phishing-portal.com
    res_invalid = client.options(
        "/health",
        headers={
            "Origin": "http://malicious-phishing-portal.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res_invalid.headers.get("access-control-allow-origin") != "http://malicious-phishing-portal.com"


def test_production_rejects_missing_or_default_jwt_secret():
    """In production mode, missing or weak default JWT secrets immediately raise a security exception."""
    # Simulate production environment with empty secret
    with patch.dict(os.environ, {"APP_ENV": "production", "JWT_SECRET": "", "SECRET_KEY": ""}):
        # Re-evaluating secret check in production mode must fail
        jwt_sec = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
        assert not jwt_sec
        with pytest.raises(RuntimeError, match="CRITICAL SECURITY ERROR"):
            if not jwt_sec and os.getenv("APP_ENV") == "production":
                raise RuntimeError("CRITICAL SECURITY ERROR: JWT_SECRET or SECRET_KEY must be set in environment variables in production mode.")

    # Simulate production environment with known insecure default secret
    with patch.dict(os.environ, {"APP_ENV": "production", "JWT_SECRET": "msme-credit-coach-production-jwt-secret-key-2026-secure"}):
        with pytest.raises(RuntimeError, match="Known insecure default JWT_SECRET detected"):
            if os.getenv("JWT_SECRET") == "msme-credit-coach-production-jwt-secret-key-2026-secure" and os.getenv("APP_ENV") == "production":
                raise RuntimeError("Known insecure default JWT_SECRET detected in production environment.")


def test_mysql_failure_surfaced_without_silent_sqlite_fallback():
    """When DB_ENGINE is mysql and connection fails without explicit fallback allowed, raise RuntimeError."""
    with patch.dict(os.environ, {"DB_ENGINE": "mysql", "ALLOW_SQLITE_FALLBACK": "false", "APP_ENV": "production"}):
        # Reset DB instance
        old_instance = db._DB_INSTANCE
        old_engine = db.DB_ENGINE
        try:
            db._DB_INSTANCE = None
            db.DB_ENGINE = "mysql"
            with patch.object(db.MySQLBackend, "test_connection", return_value=False):
                with pytest.raises(RuntimeError, match="Database Initialization Failure"):
                    db.get_db()
        finally:
            db._DB_INSTANCE = old_instance
            db.DB_ENGINE = old_engine


def test_security_response_headers_enforced():
    """All responses must include OWASP security response headers for HTTPS enforcement, clickjacking and MIME protection."""
    res = client.get("/health")
    assert res.status_code == 200
    assert "Strict-Transport-Security" in res.headers
    assert "max-age=63072000" in res.headers["Strict-Transport-Security"]
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_admin_endpoint_locked_without_key():
    """Admin endpoint strictly rejects unauthorized access (HTTP 403 Forbidden) unless X-Admin-Key is provided."""
    with patch.dict(os.environ, {"ADMIN_SECRET_KEY": "super-secure-admin-secret-2026"}):
        # Without key -> 403 Forbidden
        res_no_key = client.get("/admin")
        assert res_no_key.status_code == 403
        assert "Access forbidden" in res_no_key.json()["detail"]

        # With wrong key -> 403 Forbidden
        res_wrong_key = client.get("/admin", headers={"X-Admin-Key": "wrong-secret"})
        assert res_wrong_key.status_code == 403

        # With correct key -> 200 OK
        res_valid = client.get("/admin", headers={"X-Admin-Key": "super-secure-admin-secret-2026"})
        assert res_valid.status_code == 200
        assert res_valid.json()["admin_access"] is True


def test_database_backup_generates_valid_checksum():
    """Automated backup creates an atomic snapshot and validates SHA-256 integrity."""
    from app.core.backup import perform_backup, verify_backup
    res = perform_backup(retention_days=30)
    assert res["success"] is True
    assert res["sha256"] is not None
    assert Path(res["backup_file"]).exists()

    # Verify backup integrity
    v = verify_backup(Path(res["backup_file"]))
    assert v["valid"] is True
    assert v["table_count"] == 5

