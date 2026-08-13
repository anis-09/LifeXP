"""
LifeXP SQLite to Firestore Migration Tool

Usage:
  python scripts/migrate_to_firestore.py --dry-run
  python scripts/migrate_to_firestore.py --validate
  python scripts/migrate_to_firestore.py --resume
  python scripts/migrate_to_firestore.py --user-id <id>
"""

import argparse
import json
import logging
import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import BASE_DIR, DATABASE_PATH, FIREBASE_PROJECT_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CHECKPOINT_FILE = Path(__file__).resolve().parent / "migration_checkpoint.json"

class MigrationTool:
    def __init__(self, dry_run: bool, resume: bool, user_id: int = None):
        self.dry_run = dry_run
        self.resume = resume
        self.target_user_id = user_id
        self.checkpoint = self._load_checkpoint() if resume else {"users": {}, "global": {}}
        
        # In memory caches
        self.user_mapping = self.checkpoint.get("users", {})  # sqlite_id -> firebase_uid
        self.global_mapping = self.checkpoint.get("global", {}) # missions, achievements -> firestore_id
        
        self.db = None
        self.fs = None
        self.batch = None
        self.batch_count = 0

    def _load_checkpoint(self) -> dict:
        if CHECKPOINT_FILE.exists():
            with open(CHECKPOINT_FILE, "r") as f:
                return json.load(f)
        return {"users": {}, "global": {}}

    def _save_checkpoint(self):
        if self.dry_run:
            return
        self.checkpoint["users"] = self.user_mapping
        self.checkpoint["global"] = self.global_mapping
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump(self.checkpoint, f, indent=2)

    def _get_batch(self):
        if self.batch is None:
            self.batch = self.fs.batch()
            self.batch_count = 0
        return self.batch
        
    def _commit_batch_if_needed(self, force=False):
        if self.dry_run:
            return
        if self.batch is not None and (self.batch_count >= 500 or force):
            self.batch.commit()
            self.batch = self.fs.batch()
            self.batch_count = 0

    def run_preflight(self):
        logger.info("Running preflight checks...")
        if not DATABASE_PATH.exists():
            logger.error(f"SQLite DB not found at {DATABASE_PATH}")
            sys.exit(1)
            
        try:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if not cred_path:
                cred_path = str(BASE_DIR / "firebase-credentials.json")
            
            if not Path(cred_path).exists():
                logger.error(f"Firebase credentials not found at {cred_path}")
                sys.exit(1)
            
            project_id = os.getenv("FIREBASE_PROJECT_ID", FIREBASE_PROJECT_ID)
            
            try:
                firebase_admin.get_app()
            except ValueError:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred, {"projectId": project_id})
                
            self.fs = firestore.client()
            logger.info("Firebase connected successfully.")
        except Exception as e:
            logger.error(f"Firebase preflight failed: {e}")
            sys.exit(1)
            
        self.db = sqlite3.connect(DATABASE_PATH)
        self.db.row_factory = sqlite3.Row

    def backup_sqlite(self):
        logger.info("Backing up SQLite database...")
        backup_path = DATABASE_PATH.with_suffix(".backup.db")
        if not backup_path.exists() and not self.dry_run:
            shutil.copy2(DATABASE_PATH, backup_path)
            logger.info(f"Database backed up to {backup_path}")
        else:
            logger.info(f"Database backup already exists or dry run active.")

    def migrate_users(self):
        logger.info("Migrating Users Data (Data-Only)...")
        logger.info("Firebase Authentication migration skipped — SQLite authentication remains active.")
        
        query = "SELECT * FROM users"
        if self.target_user_id:
            query += f" WHERE id = {self.target_user_id}"
            
        rows = self.db.execute(query).fetchall()
        for row in rows:
            sqlite_id = str(row["id"])
            if self.resume and sqlite_id in self.user_mapping:
                continue
                
            uid = f"sqlite_{sqlite_id}"
            self.user_mapping[sqlite_id] = uid
            
        if self.dry_run:
            logger.info(f"[DRY RUN] Would map {len(rows)} users to Firestore without migrating authentication.")
            return

        self._save_checkpoint()
        logger.info("Users data-mapping complete.")

    def migrate_achievements(self):
        logger.info("Migrating Achievements...")
        rows = self.db.execute("SELECT * FROM achievements").fetchall()
        
        if "achievements" not in self.global_mapping:
            self.global_mapping["achievements"] = {}
            
        for row in rows:
            sqlite_id = str(row["id"])
            if self.resume and sqlite_id in self.global_mapping["achievements"]:
                continue
                
            doc_id = row["condition_key"]
            doc_ref = self.fs.collection("achievements").document(doc_id)
            data = dict(row)
            data.pop("id")
            
            if self.dry_run:
                self.global_mapping["achievements"][sqlite_id] = doc_id
                continue
                
            self._get_batch().set(doc_ref, data)
            self.batch_count += 1
            self.global_mapping["achievements"][sqlite_id] = doc_id
            self._commit_batch_if_needed()
            
        self._commit_batch_if_needed(force=True)
        self._save_checkpoint()

    def migrate_global_missions(self):
        logger.info("Migrating Missions...")
        rows = self.db.execute("SELECT m.*, c.name as category_name FROM missions m LEFT JOIN mission_categories c ON m.category_id = c.id").fetchall()
        
        if "missions" not in self.global_mapping:
            self.global_mapping["missions"] = {}
            
        for row in rows:
            sqlite_id = str(row["id"])
            if self.resume and sqlite_id in self.global_mapping["missions"]:
                continue
                
            doc_id = f"sqlite_mission_{sqlite_id}"
            doc_ref = self.fs.collection("missions").document(doc_id)
            data = dict(row)
            data.pop("id")
            data.pop("category_id")
            data["category"] = data.pop("category_name")
            if data["created_by"]:
                data["created_by"] = self.user_mapping.get(str(data["created_by"]), str(data["created_by"]))
                
            if self.dry_run:
                self.global_mapping["missions"][sqlite_id] = doc_id
                continue
                
            self._get_batch().set(doc_ref, data)
            self.batch_count += 1
            self.global_mapping["missions"][sqlite_id] = doc_id
            self._commit_batch_if_needed()
            
        self._commit_batch_if_needed(force=True)
        self._save_checkpoint()

    def migrate_user_data(self):
        logger.info("Migrating User Subcollections...")
        for sqlite_id, fb_uid in self.user_mapping.items():
            if self.target_user_id and int(sqlite_id) != self.target_user_id:
                continue
                
            user_ref = self.fs.collection("users").document(fb_uid)
            
            # 1. users doc (profile + settings) - STRICTLY NO PASSWORD DATA
            user_row = self.db.execute("SELECT * FROM users WHERE id = ?", (sqlite_id,)).fetchone()
            settings_row = self.db.execute("SELECT * FROM settings WHERE user_id = ?", (sqlite_id,)).fetchone()
            
            user_data = dict(user_row) if user_row else {}
            
            # Critical Safety: Remove sensitive auth fields
            if "id" in user_data: user_data.pop("id")
            if "password_hash" in user_data: user_data.pop("password_hash")
            
            # Safety double check: Explicit exception if it's there
            assert "password_hash" not in user_data, "CRITICAL ERROR: password_hash leaked into payload."
            
            if settings_row:
                user_data["settings"] = {
                    "theme": settings_row["theme"],
                    "language": settings_row["language"],
                    "notifications_enabled": bool(settings_row["notifications_enabled"])
                }
                
            if not self.dry_run:
                self._get_batch().set(user_ref, user_data)
                self.batch_count += 1
                
            # 2. Transactions & Period XP Aggregation
            weekly_aggregations = {}
            monthly_aggregations = {}
            
            xp_txs = self.db.execute("SELECT * FROM xp_transactions WHERE user_id = ?", (sqlite_id,)).fetchall()
            for tx in xp_txs:
                tx_data = dict(tx)
                created_at_str = tx_data.get("created_at")
                if created_at_str:
                    try:
                        tx_date = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        try:
                            tx_date = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            tx_date = datetime.utcnow()
                    
                    year, week, _ = tx_date.isocalendar()
                    w_key = f"weekly_xp_{year}_{week}"
                    m_key = f"monthly_xp_{tx_date.year}_{tx_date.month:02d}"
                    
                    amt = tx_data.get("amount", 0)
                    weekly_aggregations[w_key] = weekly_aggregations.get(w_key, 0) + amt
                    monthly_aggregations[m_key] = monthly_aggregations.get(m_key, 0) + amt
                    
                tx_id = tx_data.pop("id")
                tx_data.pop("user_id")
                tx_data["currency_type"] = "xp"
                tx_ref = user_ref.collection("transactions").document(f"xp_{tx_id}")
                if not self.dry_run:
                    self._get_batch().set(tx_ref, tx_data)
                    self.batch_count += 1
                    
            coin_txs = self.db.execute("SELECT * FROM coin_transactions WHERE user_id = ?", (sqlite_id,)).fetchall()
            for tx in coin_txs:
                tx_data = dict(tx)
                tx_id = tx_data.pop("id")
                tx_data.pop("user_id")
                tx_data["currency_type"] = "coin"
                tx_ref = user_ref.collection("transactions").document(f"coin_{tx_id}")
                if not self.dry_run:
                    self._get_batch().set(tx_ref, tx_data)
                    self.batch_count += 1
                    
            # 3. user_stats (Top-Level)
            stats_row = self.db.execute("SELECT * FROM user_stats WHERE user_id = ?", (sqlite_id,)).fetchone()
            if stats_row:
                stats_data = dict(stats_row)
                stats_data.pop("id")
                stats_data.pop("user_id")
                stats_data["full_name"] = user_data.get("full_name", "")
                stats_data["avatar"] = user_data.get("avatar", "")
                
                # Apply denormalized period aggregations
                for k, v in weekly_aggregations.items():
                    stats_data[k] = v
                for k, v in monthly_aggregations.items():
                    stats_data[k] = v
                
                stats_ref = self.fs.collection("user_stats").document(fb_uid)
                if not self.dry_run:
                    self._get_batch().set(stats_ref, stats_data)
                    self.batch_count += 1
                    
            # 4. user_missions
            missions = self.db.execute("SELECT * FROM user_missions WHERE user_id = ?", (sqlite_id,)).fetchall()
            for m in missions:
                m_data = dict(m)
                m_id = str(m_data.pop("id"))
                sqlite_mission_id = str(m_data.pop("mission_id"))
                m_data.pop("user_id")
                fb_mission_id = self.global_mapping.get("missions", {}).get(sqlite_mission_id, f"sqlite_mission_{sqlite_mission_id}")
                m_ref = user_ref.collection("missions").document(fb_mission_id)
                if not self.dry_run:
                    self._get_batch().set(m_ref, m_data)
                    self.batch_count += 1
                    
            # 5. user_achievements
            achievements = self.db.execute("SELECT * FROM user_achievements WHERE user_id = ?", (sqlite_id,)).fetchall()
            for a in achievements:
                a_data = dict(a)
                sqlite_ach_id = str(a_data.pop("achievement_id"))
                a_data.pop("user_id")
                fb_ach_id = self.global_mapping.get("achievements", {}).get(sqlite_ach_id, f"sqlite_ach_{sqlite_ach_id}")
                a_ref = user_ref.collection("achievements").document(fb_ach_id)
                if not self.dry_run:
                    self._get_batch().set(a_ref, a_data)
                    self.batch_count += 1
                    
            # 6. daily_rewards
            rewards = self.db.execute("SELECT * FROM daily_rewards WHERE user_id = ?", (sqlite_id,)).fetchall()
            for r in rewards:
                r_data = dict(r)
                r_data.pop("id")
                r_data.pop("user_id")
                day_num = str(r_data["day_number"])
                r_ref = user_ref.collection("daily_rewards").document(day_num)
                if not self.dry_run:
                    self._get_batch().set(r_ref, r_data)
                    self.batch_count += 1
                    
            # 7. notifications
            notifications = self.db.execute("SELECT * FROM notifications WHERE user_id = ?", (sqlite_id,)).fetchall()
            for n in notifications:
                n_data = dict(n)
                n_id = str(n_data.pop("id"))
                n_data.pop("user_id")
                n_ref = user_ref.collection("notifications").document(f"sqlite_notif_{n_id}")
                if not self.dry_run:
                    self._get_batch().set(n_ref, n_data)
                    self.batch_count += 1
            
            self._commit_batch_if_needed(force=True)
            logger.info(f"Migrated data for user {sqlite_id} -> {fb_uid}")

    def validate_migration(self):
        logger.info("Validating migration...")
        
        # SQLITE
        sqlite_users = self.db.execute("SELECT count(*) as c FROM users").fetchone()["c"]
        sqlite_xp = self.db.execute("SELECT sum(amount) as s FROM xp_transactions").fetchone()["s"] or 0
        sqlite_coins = self.db.execute("SELECT sum(amount) as s FROM coin_transactions").fetchone()["s"] or 0
        sqlite_tx_count = self.db.execute("SELECT count(*) as c FROM xp_transactions").fetchone()["c"]
        sqlite_tx_count += self.db.execute("SELECT count(*) as c FROM coin_transactions").fetchone()["c"]
        
        # FIRESTORE
        fs_users = len(list(self.fs.collection("users").stream()))
        fs_stats = list(self.fs.collection("user_stats").stream())
        fs_xp = sum(s.to_dict().get("current_xp", 0) for s in fs_stats)
        
        # Count transactions in firestore
        fs_tx_count = 0
        if fs_users > 0:
            for user_doc in self.fs.collection("users").stream():
                fs_tx_count += len(list(user_doc.reference.collection("transactions").stream()))
        
        logger.info("=== RECONCILIATION REPORT ===")
        logger.info(f"Users: SQLite={sqlite_users} | Firestore={fs_users}")
        logger.info(f"Total XP (Stats): SQLite={sqlite_xp} (Transactions) | Firestore={fs_xp}")
        logger.info(f"Transactions Count: SQLite={sqlite_tx_count} | Firestore={fs_tx_count}")
        
        if sqlite_users != fs_users:
            logger.warning("Mismatch in user count!")
        else:
            logger.info("User counts match!")
            
        logger.info("Authentication explicitly excluded from Firestore reconciliation.")

    def run(self):
        self.run_preflight()
        self.backup_sqlite()
        
        self.migrate_users()
        self.migrate_achievements()
        self.migrate_global_missions()
        self.migrate_user_data()
        
        if self.dry_run:
            logger.info("Dry run completed. No data was modified in Firestore.")
        else:
            logger.info("Migration completed.")
            if not self.target_user_id:
                self.validate_migration()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LifeXP SQLite to Firestore Data-Only Migration")
    parser.add_argument("--dry-run", action="store_true", help="Run without mutating Firestore")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--validate", action="store_true", help="Validate migration against SQLite")
    parser.add_argument("--user-id", type=int, help="Migrate a specific user ID")
    
    args = parser.parse_args()
    
    tool = MigrationTool(args.dry_run, args.resume, args.user_id)
    
    if args.validate:
        tool.run_preflight()
        tool.validate_migration()
    else:
        tool.run()
