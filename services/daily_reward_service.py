"""
services/daily_reward_service.py
---------------------------------
Daily Login Reward Service — Sprint 5

Business rules (from 02_LifeXP_Rules.md and approved Sprint 5 choices):
  - Users may claim exactly one reward per calendar day (server local date).
  - A 7-day cycle repeats indefinitely; day number is determined by
    counting the user's total previous claims modulo 7.
  - All XP and coin grants are routed through RewardService to maintain
    the single-source-of-truth architecture (CLAUDE.md).
  - Chest rewards grant coins + XP immediately (Phase 7 adds chest opening).
  - XP Booster (Day 6) grants XP immediately, labelled "XP Bonus".
  - Avatar Item (Day 4) is recorded in DB; no physical item granted until Phase 7.
  - Double-claim raises ValueError — never silently ignored.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from constants import DAILY_REWARD_SCHEDULE
from database.db import get_db
from services.reward_service import RewardService
from services.notification_service import NotificationService
from services.firebase_service import get_firestore_client
from flask import current_app
from firebase_admin import firestore
import datetime as dt

logger = logging.getLogger(__name__)


class DailyRewardService:
    """
    Handles all Daily Login Reward operations:
      - Checking claim status for today
      - Claiming today's reward
      - Returning the full 7-day schedule strip for the UI
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def get_reward_status(user_id: int) -> Dict:
        """
        Return the full reward status dict needed to render the rewards page
        and the dashboard card.

        Returns:
            {
                "day_number":      int  (1–7, which day in the cycle)
                "reward":          dict from DAILY_REWARD_SCHEDULE
                "claimed":         bool
                "claimed_at":      str | None (ISO timestamp if claimed)
                "seconds_until_next": int (seconds until midnight)
                "schedule":        list[dict] — 7-day strip for the UI
            }
        """
        day_number = DailyRewardService._get_next_day_number(user_id)
        reward = DAILY_REWARD_SCHEDULE[day_number]
        claim_row = DailyRewardService._get_today_claim(user_id)
        claimed = claim_row is not None
        claimed_at = claim_row["claimed_at"] if claim_row else None

        schedule = DailyRewardService._build_schedule_strip(user_id, day_number)

        return {
            "day_number":         day_number,
            "reward":             reward,
            "claimed":            claimed,
            "claimed_at":         claimed_at,
            "seconds_until_next": DailyRewardService._seconds_until_midnight(),
            "schedule":           schedule,
        }

    @staticmethod
    def claim(user_id: int) -> Dict:
        """
        Claim today's daily reward.

        Raises:
            ValueError: if already claimed today.

        Returns:
            dict with keys: day_number, reward, xp_granted, coins_granted
        """
        # Guard: one claim per calendar day
        if DailyRewardService._get_today_claim(user_id) is not None:
            raise ValueError("You already claimed today's reward. Come back tomorrow!")

        day_number = DailyRewardService._get_next_day_number(user_id)
        reward = DAILY_REWARD_SCHEDULE[day_number]

        xp_granted = reward["xp_value"]
        coins_granted = reward["coin_value"]

        firestore_enabled = current_app.config.get('FIRESTORE_DAILY_REWARDS_ENABLED', False)

        if firestore_enabled:
            fs = get_firestore_client()
            user_doc_ref = fs.collection('users').document(f'sqlite_{user_id}')
            stats_doc_ref = fs.collection('user_stats').document(f'sqlite_{user_id}')
            
            try:
                # Add to subcollection
                user_doc_ref.collection('daily_rewards').add({
                    "day_number": day_number,
                    "reward_type": reward["type"],
                    "reward_value": coins_granted or xp_granted,
                    "claimed_at": firestore.SERVER_TIMESTAMP
                })
                
                # Increment total_daily_claims in user_stats
                stats_doc_ref.set({
                    "total_daily_claims": firestore.Increment(1)
                }, merge=True)
                
                # Grant XP through RewardService
                if xp_granted > 0:
                    RewardService.grant_xp(
                        user_id=user_id,
                        amount=xp_granted,
                        source="DailyReward",
                        reference_id=day_number,
                    )

                # Grant coins through RewardService
                if coins_granted > 0:
                    RewardService.grant_coins(
                        user_id=user_id,
                        amount=coins_granted,
                        source="DailyReward",
                        reference_id=day_number,
                    )
            except Exception:
                logger.exception(
                    "Failed to claim daily reward in Firestore for user %s (day %s).",
                    user_id,
                    day_number,
                )
                raise
        else:
            db = get_db()
            try:
                # Record the claim in daily_rewards
                db.execute(
                    """
                    INSERT INTO daily_rewards (user_id, day_number, reward_type, reward_value, claimed, claimed_at)
                    VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                    """,
                    (user_id, day_number, reward["type"], coins_granted or xp_granted)
                )

                # Grant XP through RewardService (if any)
                if xp_granted > 0:
                    RewardService.grant_xp(
                        user_id=user_id,
                        amount=xp_granted,
                        source="DailyReward",
                        reference_id=day_number,
                    )

                # Grant coins through RewardService (if any)
                if coins_granted > 0:
                    RewardService.grant_coins(
                        user_id=user_id,
                        amount=coins_granted,
                        source="DailyReward",
                        reference_id=day_number,
                    )

                db.commit()

            except Exception:
                db.rollback()
                logger.exception(
                    "Failed to claim daily reward for user %s (day %s).",
                    user_id,
                    day_number,
                )
                raise

        logger.info(
            "User %s claimed Day %s reward: %s (+%s XP, +%s Coins).",
            user_id, day_number, reward["label"], xp_granted, coins_granted,
        )

        # Trigger Notification
        reward_text = []
        if xp_granted > 0:
            reward_text.append(f"{xp_granted} XP")
        if coins_granted > 0:
            reward_text.append(f"{coins_granted} Coins")
        
        NotificationService.create(
            user_id=user_id,
            title="Daily Reward Claimed",
            message=f"You claimed your Day {day_number} reward: {' and '.join(reward_text)}!",
            notif_type="Success"
        )

        return {
            "day_number":   day_number,
            "reward":       reward,
            "xp_granted":   xp_granted,
            "coins_granted": coins_granted,
        }

    @staticmethod
    def get_recent_claims(user_id: int, limit: int = 7) -> List[Dict]:
        """
        Return the most recent claim rows for a user, newest first.
        Used by the rewards page history section.
        """
        firestore_enabled = current_app.config.get('FIRESTORE_DAILY_REWARDS_ENABLED', False)

        if firestore_enabled:
            fs = get_firestore_client()
            docs = fs.collection('users').document(f'sqlite_{user_id}').collection('daily_rewards') \
                     .order_by('claimed_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            rows = []
            for d in docs:
                data = d.to_dict()
                rows.append({
                    "day_number": data.get("day_number"),
                    "reward_type": data.get("reward_type"),
                    "reward_value": data.get("reward_value"),
                    "claimed_at": data.get("claimed_at").strftime("%Y-%m-%d %H:%M:%S") if data.get("claimed_at") else None
                })
        else:
            db = get_db()
            db_rows = db.execute(
            """
            SELECT day_number, reward_type, reward_value, claimed_at
            FROM daily_rewards
            WHERE user_id = ? AND claimed = 1
            ORDER BY claimed_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        ).fetchall()
        
            rows = [dict(r) for r in db_rows]

        result = []
        for row in rows:
            row_dict = dict(row)
            day_num = row_dict["day_number"]
            sched = DAILY_REWARD_SCHEDULE.get(day_num, {})
            row_dict["label"] = sched.get("label", "Reward")
            row_dict["icon"] = sched.get("icon", "🎁")
            result.append(row_dict)

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_next_day_number(user_id: int) -> int:
        """
        Determine which day (1–7) in the cycle the user is on for their
        NEXT (current) claim.

        Logic: count all previous claims → modulo 7 → +1 maps to 1–7 range.
        The current day's unclaimed reward is based on total past claims,
        so a brand-new user gets Day 1.
        """
        firestore_enabled = current_app.config.get('FIRESTORE_DAILY_REWARDS_ENABLED', False)
        
        if firestore_enabled:
            fs = get_firestore_client()
            stats_doc = fs.collection('user_stats').document(f'sqlite_{user_id}').get()
            if stats_doc.exists:
                total_claims = stats_doc.to_dict().get("total_daily_claims", 0)
            else:
                total_claims = 0
        else:
            db = get_db()
            result = db.execute(
                """
                SELECT COUNT(*) FROM daily_rewards WHERE user_id = ? AND claimed = 1
                """,
                (user_id,)
            ).fetchone()
            total_claims = result[0] if result else 0

        # 0 past claims → Day 1, 7 past claims → Day 1 again (cycle)
        return (total_claims % 7) + 1

    @staticmethod
    def _get_today_claim(user_id: int) -> Optional[Dict]:
        """
        Return the claim row if the user has already claimed today,
        else None. Uses server local date, consistent with streak logic.
        """
        firestore_enabled = current_app.config.get('FIRESTORE_DAILY_REWARDS_ENABLED', False)

        if firestore_enabled:
            # Server local date for today
            today_start = datetime.combine(date.today(), dt.time.min).replace(tzinfo=dt.timezone.utc)
            today_end = datetime.combine(date.today(), dt.time.max).replace(tzinfo=dt.timezone.utc)
            
            fs = get_firestore_client()
            docs = fs.collection('users').document(f'sqlite_{user_id}').collection('daily_rewards') \
                     .where('claimed_at', '>=', today_start) \
                     .where('claimed_at', '<=', today_end) \
                     .order_by('claimed_at', direction=firestore.Query.DESCENDING).limit(1).stream()
            
            for d in docs:
                data = d.to_dict()
                return {
                    "day_number": data.get("day_number"),
                    "reward_type": data.get("reward_type"),
                    "reward_value": data.get("reward_value"),
                    "claimed_at": data.get("claimed_at").strftime("%Y-%m-%d %H:%M:%S") if data.get("claimed_at") else None
                }
            return None
        else:
            today = date.today().isoformat()
            db = get_db()
            row = db.execute(
                """
                SELECT id, day_number, reward_type, reward_value, claimed_at
                FROM daily_rewards
                WHERE user_id = ?
                  AND claimed = 1
                  AND DATE(claimed_at) = ?
                ORDER BY claimed_at DESC
                LIMIT 1
                """,
                (user_id, today)
            ).fetchone()
            return dict(row) if row else None

    @staticmethod
    def _seconds_until_midnight() -> int:
        """
        Return the number of whole seconds remaining until the next
        local midnight (i.e. when the next daily claim resets).
        """
        now = datetime.now()
        midnight = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return max(0, int((midnight - now).total_seconds()))

    @staticmethod
    def _build_schedule_strip(user_id: int, current_day: int) -> List[Dict]:
        """
        Build the 7-item strip shown in the rewards page UI.
        Each item indicates which days are past, today, and upcoming.

        Returns list of dicts:
            {
                "day_number": int,
                "label":      str,
                "icon":       str,
                "state":      "past" | "today" | "upcoming",
            }
        """
        firestore_enabled = current_app.config.get('FIRESTORE_DAILY_REWARDS_ENABLED', False)
        
        if firestore_enabled:
            fs = get_firestore_client()
            stats_doc = fs.collection('user_stats').document(f'sqlite_{user_id}').get()
            if stats_doc.exists:
                total_claimed = stats_doc.to_dict().get("total_daily_claims", 0)
            else:
                total_claimed = 0
        else:
            db = get_db()
            # Count total claimed rewards to determine offset in the cycle
            result = db.execute(
                "SELECT COUNT(*) FROM daily_rewards WHERE user_id = ? AND claimed = 1",
                (user_id,)
            ).fetchone()
            total_claimed = result[0] if result else 0

        strip = []
        for day_num in range(1, 8):
            sched = DAILY_REWARD_SCHEDULE[day_num]
            # A day is "past" if it falls before current_day in this cycle
            # current_day is the day currently being shown (unclaimed)
            if day_num < current_day:
                state = "past"
            elif day_num == current_day:
                state = "today"
            else:
                state = "upcoming"

            strip.append({
                "day_number": day_num,
                "label":      sched["label"],
                "icon":       sched["icon"],
                "state":      state,
            })

        return strip
