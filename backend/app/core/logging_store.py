"""
Self-logging + streak tracking for the MSME Credit Score Improvement Coach.

Uses SQLite directly (no ORM) — deliberately simple for Phase 2. This is
real, persistent storage (survives restarts, unlike an in-memory dict), but
swapping to PostgreSQL later just means changing this one file.
"""

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "app_data.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logged_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id TEXT NOT NULL,
            factor TEXT NOT NULL,
            description TEXT NOT NULL,
            logged_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_action(owner_id: str, factor: str, description: str, logged_at: str = None) -> dict:
    """logged_at is normally auto-set to now; the override exists only so tests
    can simulate actions happening in past weeks without waiting real time."""
    conn = sqlite3.connect(DB_PATH)
    logged_at = logged_at or datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO logged_actions (owner_id, factor, description, logged_at) VALUES (?, ?, ?, ?)",
        (owner_id, factor, description, logged_at),
    )
    conn.commit()
    action_id = cur.lastrowid
    conn.close()
    return {"id": action_id, "owner_id": owner_id, "factor": factor,
            "description": description, "logged_at": logged_at}


def get_actions(owner_id: str) -> list:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM logged_actions WHERE owner_id = ? ORDER BY logged_at DESC", (owner_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def compute_streak_weeks(owner_id: str) -> int:
    """
    Consecutive calendar weeks (Mon-Sun) with at least one logged action,
    counted backward from the most recent logged week. A gap of even one
    week breaks the streak.
    """
    actions = get_actions(owner_id)
    if not actions:
        return 0

    weeks_with_activity = set()
    for a in actions:
        dt = datetime.fromisoformat(a["logged_at"])
        iso_year, iso_week, _ = dt.isocalendar()
        weeks_with_activity.add((iso_year, iso_week))

    most_recent_year, most_recent_week = max(weeks_with_activity)
    streak = 0
    current = datetime.fromisocalendar(most_recent_year, most_recent_week, 1)  # Monday of that week
    while (current.isocalendar()[0], current.isocalendar()[1]) in weeks_with_activity:
        streak += 1
        current -= timedelta(weeks=1)
    return streak


def reset_db_for_testing() -> None:
    """Only for local testing — wipes all logged actions."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM logged_actions")
    conn.commit()
    conn.close()
