"""
Unified Database Adapter for MSME Credit Score Improvement Coach.

Supports:
1. MySQL Server 8.0+ (Production target via PyMySQL)
2. SQLite (Transparent local fallback if MySQL credentials are not yet configured)
"""

import os
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
from dataclasses import is_dataclass, asdict

def _json_serial(obj):
    if is_dataclass(obj):
        return asdict(obj)
    return str(obj)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except Exception:
    pass

DB_ENGINE = os.getenv("DB_ENGINE", "mysql").lower()
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "msme_credit_coach")
MYSQL_SSL = os.getenv("MYSQL_SSL", "false").lower() in ("true", "1", "yes")

SQLITE_PATH = Path(__file__).resolve().parent / "app_data.db"

try:
    from app.core import security
except ModuleNotFoundError:
    import security


def hash_password(password: str) -> str:
    """Hash password using Argon2id with unique salt."""
    return security.hash_password(password)


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify password against stored hash (Argon2id or legacy SHA-256)."""
    return security.verify_password(stored_hash, password)


# =====================================================================
# MySQL Backend Implementation (PyMySQL)
# =====================================================================

class MySQLBackend:
    def __init__(self):
        import pymysql
        import pymysql.cursors
        self._pymysql = pymysql
        self._cursor_class = pymysql.cursors.DictCursor

    def get_connection(self):
        kwargs = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "database": MYSQL_DATABASE,
            "cursorclass": self._cursor_class,
            "autocommit": True,
            "connect_timeout": 5,
        }
        if MYSQL_SSL:
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            kwargs["ssl"] = ctx
        return self._pymysql.connect(**kwargs)

    def test_connection(self) -> bool:
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            return True
        except Exception:
            return False

    def init_db(self) -> None:
        """Ensures all 5 tables exist on the connected MySQL server."""
        try:
            conn = self.get_connection()
            schema_path = Path(__file__).resolve().parent.parent.parent / "schema.sql"
            if schema_path.exists():
                with open(schema_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                with conn.cursor() as cur:
                    for stmt in sql_script.split(";"):
                        cleaned = stmt.strip()
                        # Skip database creation/switching statements if already inside target database
                        if cleaned and not cleaned.lower().startswith("create database") and not cleaned.lower().startswith("use "):
                            try:
                                cur.execute(cleaned)
                            except Exception:
                                pass
                    # Safe schema upgrade: ensure is_demo column exists
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN is_demo BOOLEAN DEFAULT FALSE")
                    except Exception:
                        pass
                    # Safe schema upgrade: separate official CMR from estimated CMR in cibil_cir_reports
                    for col, col_type in [
                        ("official_cmr_rank", "TINYINT UNSIGNED DEFAULT NULL"),
                        ("estimated_cmr_rank", "TINYINT UNSIGNED DEFAULT NULL"),
                        ("report_date", "VARCHAR(64) DEFAULT NULL"),
                        ("data_provenance", "VARCHAR(64) DEFAULT 'user_upload'"),
                    ]:
                        try:
                            cur.execute(f"ALTER TABLE cibil_cir_reports ADD COLUMN {col} {col_type}")
                        except Exception:
                            pass
            conn.close()
        except Exception as e:
            print(f"[DB] Notice during MySQL init_db: {e}")

    def create_user(
        self,
        owner_id: str,
        full_name: str,
        business_name: str,
        phone: str,
        email: str,
        password: str,
        target_rank: int = 3,
        industry_category: str = "medium",
        is_demo: bool = False,
    ) -> Dict[str, Any]:
        clean_phone = phone.strip()
        clean_email = email.strip().lower()
        pwd_hash = hash_password(password)

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                # Check duplicate
                cur.execute(
                    "SELECT id FROM users WHERE phone = %s OR email = %s",
                    (clean_phone, clean_email),
                )
                if cur.fetchone():
                    raise ValueError("An account with this mobile number or email address already exists.")

                cur.execute(
                    """
                    INSERT INTO users (owner_id, full_name, business_name, phone, email, password_hash, target_rank, industry_category, is_demo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (owner_id, full_name, business_name, clean_phone, clean_email, pwd_hash, target_rank, industry_category, is_demo),
                )
                user_id = cur.lastrowid

                # Create default empty business credit profile
                cur.execute(
                    """
                    INSERT INTO business_credit_profiles (owner_id, industry_risk_category, source)
                    VALUES (%s, %s, 'unranked')
                    ON DUPLICATE KEY UPDATE industry_risk_category = VALUES(industry_risk_category)
                    """,
                    (owner_id, industry_category),
                )

                # Create default alternate data signals
                cur.execute(
                    """
                    INSERT INTO alternate_data_signals (owner_id, gst_filing_regularity, upi_inflow_stability, signal_tier)
                    VALUES (%s, 0.800, 0.800, 'Moderate Cash-Flow Stability')
                    ON DUPLICATE KEY UPDATE gst_filing_regularity = VALUES(gst_filing_regularity)
                    """,
                    (owner_id,),
                )

            return {
                "id": user_id,
                "owner_id": owner_id,
                "full_name": full_name,
                "business_name": business_name,
                "phone": clean_phone,
                "email": clean_email,
                "email_or_phone": clean_email,
                "target_rank": target_rank,
                "industry_category": industry_category,
                "is_demo": bool(is_demo),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        finally:
            conn.close()

    def authenticate_user(self, identifier: str, password: str) -> Optional[Dict[str, Any]]:
        raw_id = identifier.strip()
        clean_lower = raw_id.lower()
        digits = re.sub(r"\D", "", raw_id)
        last_10 = digits[-10:] if len(digits) >= 10 else digits

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT * FROM users
                    WHERE (
                        email = %s
                        OR phone = %s
                        OR (%s != '' AND length(%s) >= 10 AND phone LIKE %s)
                    )
                    LIMIT 1
                    """,
                    (clean_lower, raw_id, digits, digits, f"%{last_10}"),
                )
                row = cur.fetchone()
                if not row:
                    return None
                
                stored_hash = row.get("password_hash", "")
                if not verify_password(stored_hash, password):
                    return None

                if "password_hash" in row:
                    del row["password_hash"]
                row["is_demo"] = bool(row.get("is_demo", False))
                return row
        finally:
            conn.close()

    def get_user_by_owner_id(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE owner_id = %s LIMIT 1", (owner_id,))
                row = cur.fetchone()
                if not row:
                    return None
                if "password_hash" in row:
                    del row["password_hash"]
                return row
        finally:
            conn.close()

    def save_business_profile(self, owner_id: str, data: Dict[str, Any]) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO business_credit_profiles (
                        owner_id, on_time_payment_pct, has_recent_delinquency,
                        credit_utilization, credit_tenure_years, business_age_years,
                        industry_risk_category, estimated_cmr_rank, overall_proxy_score, source
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        on_time_payment_pct = VALUES(on_time_payment_pct),
                        has_recent_delinquency = VALUES(has_recent_delinquency),
                        credit_utilization = VALUES(credit_utilization),
                        credit_tenure_years = VALUES(credit_tenure_years),
                        business_age_years = VALUES(business_age_years),
                        industry_risk_category = VALUES(industry_risk_category),
                        estimated_cmr_rank = VALUES(estimated_cmr_rank),
                        overall_proxy_score = VALUES(overall_proxy_score),
                        source = VALUES(source)
                    """,
                    (
                        owner_id,
                        data.get("on_time_payment_pct"),
                        data.get("has_recent_delinquency"),
                        data.get("credit_utilization"),
                        data.get("credit_tenure_years"),
                        data.get("business_age_years"),
                        data.get("industry_risk_category", "medium"),
                        data.get("estimated_cmr_rank"),
                        data.get("overall_proxy_score"),
                        data.get("source", "manual_sandbox"),
                    ),
                )
        finally:
            conn.close()

    def get_business_profile(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM business_credit_profiles WHERE owner_id = %s LIMIT 1", (owner_id,))
                return cur.fetchone()
        finally:
            conn.close()

    def save_cibil_report(
        self,
        owner_id: str,
        filename: str,
        rcn: Optional[str] = None,
        company_name: Optional[str] = None,
        pan: Optional[str] = None,
        gstin: Optional[str] = None,
        cmr_rank: Optional[int] = None,
        total_sanctioned: float = 0.0,
        total_balance: float = 0.0,
        total_overdue: float = 0.0,
        extracted_payload: Optional[Dict[str, Any]] = None,
        official_cmr_rank: Optional[int] = None,
        estimated_cmr_rank: Optional[int] = None,
        report_date: Optional[str] = None,
        data_provenance: str = "user_upload",
    ) -> int:
        eff_official = official_cmr_rank if official_cmr_rank is not None else cmr_rank
        stored_cmr = eff_official if eff_official is not None else 0
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                try:
                    cur.execute(
                        """
                        INSERT INTO cibil_cir_reports (
                            owner_id, filename, rcn, company_name, pan, gstin,
                            cmr_rank, official_cmr_rank, estimated_cmr_rank, report_date, data_provenance,
                            total_sanctioned, total_balance, total_overdue, extracted_payload
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            owner_id,
                            filename,
                            rcn,
                            company_name,
                            pan,
                            gstin,
                            stored_cmr,
                            official_cmr_rank,
                            estimated_cmr_rank,
                            report_date,
                            data_provenance,
                            total_sanctioned,
                            total_balance,
                            total_overdue,
                            json.dumps(extracted_payload, default=_json_serial) if extracted_payload else None,
                        ),
                    )
                except Exception:
                    cur.execute(
                        """
                        INSERT INTO cibil_cir_reports (
                            owner_id, filename, rcn, company_name, pan, gstin,
                            cmr_rank, total_sanctioned, total_balance, total_overdue, extracted_payload
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            owner_id,
                            filename,
                            rcn,
                            company_name,
                            pan,
                            gstin,
                            stored_cmr,
                            total_sanctioned,
                            total_balance,
                            total_overdue,
                            json.dumps(extracted_payload, default=_json_serial) if extracted_payload else None,
                        ),
                    )
                return cur.lastrowid
        finally:
            conn.close()

    def get_cibil_reports(self, owner_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM cibil_cir_reports WHERE owner_id = %s ORDER BY uploaded_at DESC", (owner_id,))
                rows = cur.fetchall()
                for r in rows:
                    if r.get("extracted_payload") and isinstance(r["extracted_payload"], str):
                        try:
                            r["extracted_payload"] = json.loads(r["extracted_payload"])
                        except Exception:
                            pass
                return rows
        finally:
            conn.close()

    def log_action(self, owner_id: str, factor: str, description: str, logged_at: Optional[str] = None) -> Dict[str, Any]:
        conn = self.get_connection()
        ts = logged_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO logged_actions (owner_id, factor, description, logged_at) VALUES (%s, %s, %s, %s)",
                    (owner_id, factor, description, ts),
                )
                action_id = cur.lastrowid
            return {
                "id": action_id,
                "owner_id": owner_id,
                "factor": factor,
                "description": description,
                "logged_at": ts,
            }
        finally:
            conn.close()

    def get_actions(self, owner_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM logged_actions WHERE owner_id = %s ORDER BY logged_at DESC", (owner_id,))
                rows = cur.fetchall()
                for r in rows:
                    if isinstance(r.get("logged_at"), datetime):
                        r["logged_at"] = r["logged_at"].isoformat()
                return rows
        finally:
            conn.close()

    def compute_streak_weeks(self, owner_id: str) -> int:
        actions = self.get_actions(owner_id)
        if not actions:
            return 0
        weeks = set()
        for a in actions:
            try:
                dt_str = str(a["logged_at"]).replace("Z", "+00:00")
                dt = datetime.fromisoformat(dt_str)
                weeks.add((dt.isocalendar()[0], dt.isocalendar()[1]))
            except Exception:
                continue
        if not weeks:
            return 0
        most_recent_year, most_recent_week = max(weeks)
        streak = 0
        current = datetime.fromisocalendar(most_recent_year, most_recent_week, 1)
        while (current.isocalendar()[0], current.isocalendar()[1]) in weeks:
            streak += 1
            current -= timedelta(weeks=1)
        return streak

    def delete_action(self, action_id: int, owner_id: str) -> bool:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM logged_actions WHERE id = %s AND owner_id = %s", (action_id, owner_id))
                return cur.rowcount > 0
        finally:
            conn.close()

    def reset_actions_for_owner(self, owner_id: str) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM logged_actions WHERE owner_id = %s", (owner_id,))
        finally:
            conn.close()

    def save_alternate_signals(self, owner_id: str, gst: float, upi: float, tier: str) -> None:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO alternate_data_signals (owner_id, gst_filing_regularity, upi_inflow_stability, signal_tier)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        gst_filing_regularity = VALUES(gst_filing_regularity),
                        upi_inflow_stability = VALUES(upi_inflow_stability),
                        signal_tier = VALUES(signal_tier)
                    """,
                    (owner_id, gst, upi, tier),
                )
        finally:
            conn.close()

    def get_alternate_signals(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM alternate_data_signals WHERE owner_id = %s LIMIT 1", (owner_id,))
                return cur.fetchone()
        finally:
            conn.close()


# =====================================================================
# SQLite Backend Implementation (Lightweight Fallback)
# =====================================================================

class SQLiteBackend:
    def __init__(self, db_path: Path = SQLITE_PATH):
        import sqlite3
        self._sqlite3 = sqlite3
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = self._sqlite3.connect(self.db_path)
        conn.row_factory = self._sqlite3.Row
        return conn

    def test_connection(self) -> bool:
        return True

    def init_db(self) -> None:
        conn = self._sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                business_name TEXT NOT NULL,
                email_or_phone TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                password_hash TEXT NOT NULL,
                target_rank INTEGER DEFAULT 3,
                industry_category TEXT DEFAULT 'medium',
                created_at TEXT NOT NULL
            )
        """)
        # Ensure migration columns exist on existing users table
        for col_name, col_type in [
            ("phone", "TEXT"),
            ("email", "TEXT"),
            ("target_rank", "INTEGER DEFAULT 3"),
            ("industry_category", "TEXT DEFAULT 'medium'"),
            ("is_demo", "INTEGER DEFAULT 0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            except Exception:
                pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS business_credit_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT UNIQUE NOT NULL,
                on_time_payment_pct REAL,
                has_recent_delinquency INTEGER,
                credit_utilization REAL,
                credit_tenure_years REAL,
                business_age_years REAL,
                industry_risk_category TEXT DEFAULT 'medium',
                estimated_cmr_rank INTEGER,
                overall_proxy_score REAL,
                source TEXT DEFAULT 'unranked',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cibil_cir_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                rcn TEXT,
                company_name TEXT,
                pan TEXT,
                gstin TEXT,
                cmr_rank INTEGER NOT NULL,
                official_cmr_rank INTEGER DEFAULT NULL,
                estimated_cmr_rank INTEGER DEFAULT NULL,
                report_date TEXT DEFAULT NULL,
                data_provenance TEXT DEFAULT 'user_upload',
                total_sanctioned REAL DEFAULT 0,
                total_balance REAL DEFAULT 0,
                total_overdue REAL DEFAULT 0,
                extracted_payload TEXT,
                uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Safe schema migration for SQLite
        for col, col_type in [
            ("official_cmr_rank", "INTEGER DEFAULT NULL"),
            ("estimated_cmr_rank", "INTEGER DEFAULT NULL"),
            ("report_date", "TEXT DEFAULT NULL"),
            ("data_provenance", "TEXT DEFAULT 'user_upload'"),
        ]:
            try:
                conn.execute(f"ALTER TABLE cibil_cir_reports ADD COLUMN {col} {col_type}")
                conn.commit()
            except Exception:
                pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logged_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT NOT NULL,
                factor TEXT NOT NULL,
                description TEXT NOT NULL,
                logged_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alternate_data_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id TEXT UNIQUE NOT NULL,
                gst_filing_regularity REAL DEFAULT 0.800,
                upi_inflow_stability REAL DEFAULT 0.800,
                signal_tier TEXT DEFAULT 'Moderate Cash-Flow Stability',
                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def create_user(
        self,
        owner_id: str,
        full_name: str,
        business_name: str,
        phone: str,
        email: str,
        password: str,
        target_rank: int = 3,
        industry_category: str = "medium",
        is_demo: bool = False,
    ) -> Dict[str, Any]:
        clean_phone = phone.strip()
        clean_email = email.strip().lower()
        pwd_hash = hash_password(password)
        created_at = datetime.now(timezone.utc).isoformat()

        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id FROM users
            WHERE (phone IS NOT NULL AND phone != '' AND phone = ?)
               OR (email IS NOT NULL AND email != '' AND email = ?)
               OR email_or_phone = ?
               OR email_or_phone = ?
            """,
            (clean_phone, clean_email, clean_phone, clean_email),
        )
        if cur.fetchone():
            conn.close()
            raise ValueError("An account with this mobile number or email address already exists.")

        try:
            cur = conn.execute(
                """
                INSERT INTO users (owner_id, full_name, business_name, email_or_phone, phone, email, password_hash, target_rank, industry_category, is_demo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (owner_id, full_name, business_name, clean_email, clean_phone, clean_email, pwd_hash, target_rank, industry_category, 1 if is_demo else 0, created_at),
            )
            conn.commit()
            user_id = cur.lastrowid
            conn.close()
            return {
                "id": user_id,
                "owner_id": owner_id,
                "full_name": full_name,
                "business_name": business_name,
                "phone": clean_phone,
                "email": clean_email,
                "email_or_phone": clean_email,
                "target_rank": target_rank,
                "industry_category": industry_category,
                "is_demo": bool(is_demo),
                "created_at": created_at,
            }
        except Exception as e:
            conn.close()
            raise ValueError(f"Could not create account: {str(e)}")

    def authenticate_user(self, identifier: str, password: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        raw_id = identifier.strip()
        clean_lower = raw_id.lower()
        digits = re.sub(r"\D", "", raw_id)
        last_10 = digits[-10:] if len(digits) >= 10 else digits

        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM users
            WHERE (
                email = ?
                OR phone = ?
                OR email_or_phone = ?
                OR (phone IS NOT NULL AND phone != '' AND length(?) >= 10 AND phone LIKE ?)
            )
            LIMIT 1
            """,
            (clean_lower, raw_id, clean_lower, digits, f"%{last_10}"),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        stored_hash = d.get("password_hash", "")
        if not verify_password(stored_hash, password):
            return None
        if "password_hash" in d:
            del d["password_hash"]
        d["is_demo"] = bool(d.get("is_demo", 0))
        return d

    def get_user_by_owner_id(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM users WHERE owner_id = ?", (owner_id,)).fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if "password_hash" in d:
            del d["password_hash"]
        return d

    def save_business_profile(self, owner_id: str, data: Dict[str, Any]) -> None:
        conn = self.get_connection()
        conn.execute(
            """
            INSERT INTO business_credit_profiles (
                owner_id, on_time_payment_pct, has_recent_delinquency,
                credit_utilization, credit_tenure_years, business_age_years,
                industry_risk_category, estimated_cmr_rank, overall_proxy_score, source
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(owner_id) DO UPDATE SET
                on_time_payment_pct = excluded.on_time_payment_pct,
                has_recent_delinquency = excluded.has_recent_delinquency,
                credit_utilization = excluded.credit_utilization,
                credit_tenure_years = excluded.credit_tenure_years,
                business_age_years = excluded.business_age_years,
                industry_risk_category = excluded.industry_risk_category,
                estimated_cmr_rank = excluded.estimated_cmr_rank,
                overall_proxy_score = excluded.overall_proxy_score,
                source = excluded.source
            """,
            (
                owner_id,
                data.get("on_time_payment_pct"),
                1 if data.get("has_recent_delinquency") else 0,
                data.get("credit_utilization"),
                data.get("credit_tenure_years"),
                data.get("business_age_years"),
                data.get("industry_risk_category", "medium"),
                data.get("estimated_cmr_rank"),
                data.get("overall_proxy_score"),
                data.get("source", "manual_sandbox"),
            ),
        )
        conn.commit()
        conn.close()

    def get_business_profile(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM business_credit_profiles WHERE owner_id = ?", (owner_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def save_cibil_report(
        self,
        owner_id: str,
        filename: str,
        rcn: Optional[str] = None,
        company_name: Optional[str] = None,
        pan: Optional[str] = None,
        gstin: Optional[str] = None,
        cmr_rank: Optional[int] = None,
        total_sanctioned: float = 0.0,
        total_balance: float = 0.0,
        total_overdue: float = 0.0,
        extracted_payload: Optional[Dict[str, Any]] = None,
        official_cmr_rank: Optional[int] = None,
        estimated_cmr_rank: Optional[int] = None,
        report_date: Optional[str] = None,
        data_provenance: str = "user_upload",
    ) -> int:
        eff_official = official_cmr_rank if official_cmr_rank is not None else cmr_rank
        stored_cmr = eff_official if eff_official is not None else 0
        conn = self.get_connection()
        try:
            cur = conn.execute(
                """
                INSERT INTO cibil_cir_reports (
                    owner_id, filename, rcn, company_name, pan, gstin,
                    cmr_rank, official_cmr_rank, estimated_cmr_rank, report_date, data_provenance,
                    total_sanctioned, total_balance, total_overdue, extracted_payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    owner_id,
                    filename,
                    rcn,
                    company_name,
                    pan,
                    gstin,
                    stored_cmr,
                    official_cmr_rank,
                    estimated_cmr_rank,
                    report_date,
                    data_provenance,
                    total_sanctioned,
                    total_balance,
                    total_overdue,
                    json.dumps(extracted_payload, default=_json_serial) if extracted_payload else None,
                ),
            )
        except Exception:
            cur = conn.execute(
                """
                INSERT INTO cibil_cir_reports (
                    owner_id, filename, rcn, company_name, pan, gstin,
                    cmr_rank, total_sanctioned, total_balance, total_overdue, extracted_payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    owner_id,
                    filename,
                    rcn,
                    company_name,
                    pan,
                    gstin,
                    stored_cmr,
                    total_sanctioned,
                    total_balance,
                    total_overdue,
                    json.dumps(extracted_payload, default=_json_serial) if extracted_payload else None,
                ),
            )
        conn.commit()
        row_id = cur.lastrowid
        conn.close()
        return row_id

    def get_cibil_reports(self, owner_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM cibil_cir_reports WHERE owner_id = ? ORDER BY uploaded_at DESC", (owner_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            if d.get("extracted_payload"):
                try:
                    d["extracted_payload"] = json.loads(d["extracted_payload"])
                except Exception:
                    pass
            result.append(d)
        conn.close()
        return result

    def log_action(self, owner_id: str, factor: str, description: str, logged_at: Optional[str] = None) -> Dict[str, Any]:
        conn = self.get_connection()
        ts = logged_at or datetime.now(timezone.utc).isoformat()
        cur = conn.execute(
            "INSERT INTO logged_actions (owner_id, factor, description, logged_at) VALUES (?, ?, ?, ?)",
            (owner_id, factor, description, ts),
        )
        conn.commit()
        action_id = cur.lastrowid
        conn.close()
        return {
            "id": action_id,
            "owner_id": owner_id,
            "factor": factor,
            "description": description,
            "logged_at": ts,
        }

    def get_actions(self, owner_id: str) -> List[Dict[str, Any]]:
        conn = self.get_connection()
        rows = conn.execute("SELECT * FROM logged_actions WHERE owner_id = ? ORDER BY logged_at DESC", (owner_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def compute_streak_weeks(self, owner_id: str) -> int:
        actions = self.get_actions(owner_id)
        if not actions:
            return 0
        weeks = set()
        for a in actions:
            try:
                dt = datetime.fromisoformat(str(a["logged_at"]).replace("Z", "+00:00"))
                weeks.add((dt.isocalendar()[0], dt.isocalendar()[1]))
            except Exception:
                continue
        if not weeks:
            return 0
        most_recent_year, most_recent_week = max(weeks)
        streak = 0
        current = datetime.fromisocalendar(most_recent_year, most_recent_week, 1)
        while (current.isocalendar()[0], current.isocalendar()[1]) in weeks:
            streak += 1
            current -= timedelta(weeks=1)
        return streak

    def delete_action(self, action_id: int, owner_id: str) -> bool:
        conn = self.get_connection()
        cur = conn.execute("DELETE FROM logged_actions WHERE id = ? AND owner_id = ?", (action_id, owner_id))
        conn.commit()
        affected = cur.rowcount
        conn.close()
        return affected > 0

    def reset_actions_for_owner(self, owner_id: str) -> None:
        conn = self.get_connection()
        conn.execute("DELETE FROM logged_actions WHERE owner_id = ?", (owner_id,))
        conn.commit()
        conn.close()

    def save_alternate_signals(self, owner_id: str, gst: float, upi: float, tier: str) -> None:
        conn = self.get_connection()
        conn.execute(
            """
            INSERT INTO alternate_data_signals (owner_id, gst_filing_regularity, upi_inflow_stability, signal_tier)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(owner_id) DO UPDATE SET
                gst_filing_regularity = excluded.gst_filing_regularity,
                upi_inflow_stability = excluded.upi_inflow_stability,
                signal_tier = excluded.signal_tier
            """,
            (owner_id, gst, upi, tier),
        )
        conn.commit()
        conn.close()

    def get_alternate_signals(self, owner_id: str) -> Optional[Dict[str, Any]]:
        conn = self.get_connection()
        row = conn.execute("SELECT * FROM alternate_data_signals WHERE owner_id = ?", (owner_id,)).fetchone()
        conn.close()
        return dict(row) if row else None


# =====================================================================
# Database Factory & Singleton
# =====================================================================

_DB_INSTANCE = None
_ACTIVE_ENGINE = "sqlite"


def get_db():
    global _DB_INSTANCE, _ACTIVE_ENGINE
    if _DB_INSTANCE is not None:
        return _DB_INSTANCE

    if DB_ENGINE == "mysql":
        try:
            backend = MySQLBackend()
            if backend.test_connection():
                _DB_INSTANCE = backend
                _ACTIVE_ENGINE = "mysql"
                print(f"[DB] Connected successfully to MySQL ({MYSQL_DATABASE}@{MYSQL_HOST}:{MYSQL_PORT})")
                return _DB_INSTANCE
            else:
                print(f"[DB Notice] Could not connect to MySQL Server ({MYSQL_HOST}:{MYSQL_PORT}). "
                      f"Using SQLite fallback ({SQLITE_PATH.name}). Set MYSQL_PASSWORD in backend/.env to connect.")
        except Exception as e:
            print(f"[DB Notice] MySQL initialization error: {e}. Falling back to SQLite.")

    # Fallback
    _DB_INSTANCE = SQLiteBackend()
    _ACTIVE_ENGINE = "sqlite"
    return _DB_INSTANCE


def get_active_engine_info() -> Dict[str, Any]:
    get_db()
    return {
        "engine": _ACTIVE_ENGINE,
        "mysql_configured": bool(MYSQL_PASSWORD),
        "mysql_host": f"{MYSQL_HOST}:{MYSQL_PORT}",
        "mysql_database": MYSQL_DATABASE,
        "mysql_user": MYSQL_USER,
        "sqlite_path": str(SQLITE_PATH),
    }
