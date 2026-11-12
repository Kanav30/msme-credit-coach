"""
Self-logging + streak tracking & user storage for the MSME Credit Score Improvement Coach.

Delegates to db.py adapter, which automatically connects to MySQL 8.0+ when configured,
with transparent SQLite fallback if credentials are pending.
"""

from typing import Optional, Dict, Any, List

try:
    from app.core import db
except ModuleNotFoundError:
    import db


def init_db() -> None:
    db.get_db().init_db()


def hash_password(password: str) -> str:
    return db.hash_password(password)


def create_user(
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
    return db.get_db().create_user(
        owner_id=owner_id,
        full_name=full_name,
        business_name=business_name,
        phone=phone,
        email=email,
        password=password,
        target_rank=target_rank,
        industry_category=industry_category,
        is_demo=is_demo,
    )


def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    return db.get_db().authenticate_user(identifier, password)


def get_user_by_owner_id(owner_id: str) -> Optional[Dict[str, Any]]:
    return db.get_db().get_user_by_owner_id(owner_id)


def save_business_profile(owner_id: str, data: Dict[str, Any]) -> None:
    db.get_db().save_business_profile(owner_id, data)


def get_business_profile(owner_id: str) -> Optional[Dict[str, Any]]:
    return db.get_db().get_business_profile(owner_id)


def save_cibil_report(
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
    illustrative_cmr_rank: Optional[int] = None,
    rank_source: Optional[str] = None,
    estimated_cmr_rank: Optional[int] = None,
    report_date: Optional[str] = None,
    data_provenance: str = "user_upload",
) -> int:
    return db.get_db().save_cibil_report(
        owner_id=owner_id,
        filename=filename,
        rcn=rcn,
        company_name=company_name,
        pan=pan,
        gstin=gstin,
        cmr_rank=cmr_rank,
        total_sanctioned=total_sanctioned,
        total_balance=total_balance,
        total_overdue=total_overdue,
        extracted_payload=extracted_payload,
        official_cmr_rank=official_cmr_rank,
        illustrative_cmr_rank=illustrative_cmr_rank,
        rank_source=rank_source,
        estimated_cmr_rank=estimated_cmr_rank,
        report_date=report_date,
        data_provenance=data_provenance,
    )


def get_cibil_reports(owner_id: str) -> List[Dict[str, Any]]:
    return db.get_db().get_cibil_reports(owner_id)


def log_action(owner_id: str, factor: str, description: str, logged_at: Optional[str] = None) -> Dict[str, Any]:
    return db.get_db().log_action(owner_id, factor, description, logged_at)


def get_actions(owner_id: str) -> List[Dict[str, Any]]:
    return db.get_db().get_actions(owner_id)


def compute_streak_weeks(owner_id: str) -> int:
    return db.get_db().compute_streak_weeks(owner_id)


def reset_actions_for_owner(owner_id: str) -> None:
    db.get_db().reset_actions_for_owner(owner_id)


def reset_owner_data(owner_id: str) -> None:
    """Transactionally clears all business profiles, CIBIL reports, alternate data signals, and actions for owner."""
    db.get_db().reset_owner_data(owner_id)


def delete_action(action_id: int, owner_id: str) -> bool:
    return db.get_db().delete_action(action_id, owner_id)


def save_alternate_signals(owner_id: str, gst: float, upi: float, tier: str) -> None:
    db.get_db().save_alternate_signals(owner_id, gst, upi, tier)


def get_alternate_signals(owner_id: str) -> Optional[Dict[str, Any]]:
    return db.get_db().get_alternate_signals(owner_id)


def get_active_engine_info() -> Dict[str, Any]:
    return db.get_active_engine_info()


def reset_db_for_testing() -> None:
    pass
