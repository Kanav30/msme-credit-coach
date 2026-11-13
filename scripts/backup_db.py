#!/usr/bin/env python3
"""
MSME Credit Score Improvement Coach — Database Backup CLI.
Can be executed manually or as a scheduled cron job / Windows Task.
Usage:
    python scripts/backup_db.py --backup
    python scripts/backup_db.py --list
    python scripts/backup_db.py --verify <backup_file_path>
"""

import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir / "app"))
sys.path.insert(0, str(backend_dir / "app" / "core"))

from app.core.backup import perform_backup, list_backups, verify_backup

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="MSME Credit Coach — Database Backup CLI")
    parser.add_argument("--backup", action="store_true", default=True, help="Execute an immediate database backup (default)")
    parser.add_argument("--list", action="store_true", help="List all stored backups")
    parser.add_argument("--verify", type=str, help="Verify the integrity of a backup file")
    parser.add_argument("--retention", type=int, default=30, help="Backup retention period in days (default: 30)")

    args = parser.parse_args()

    if args.list:
        bkps = list_backups()
        print(f"\n[MSME Backup Manager] Found {len(bkps)} backup archive(s):")
        for b in bkps:
            print(f"  • {b['filename']} ({b['size_bytes']} bytes, Modified: {b['modified']})")
    elif args.verify:
        v = verify_backup(Path(args.verify))
        print("\n[MSME Backup Manager] Verification Result:")
        print(json.dumps(v, indent=2))
    else:
        print("\n[MSME Backup Manager] Initiating automated database backup...")
        res = perform_backup(retention_days=args.retention)
        print("[MSME Backup Manager] Backup complete:")
        print(json.dumps(res, indent=2))
