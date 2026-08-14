# Phase 6 Firestore Integration Plan

## Objective
Perform a deep architectural inspection and plan the next Firestore integration phase (Phase 6). The goal is to select the safest and most logical module to migrate from SQLite to Firestore, ensuring no data loss, backward compatibility, and minimal risk.

## Current Architecture Status
- **SQLite-Only**: `users` (Auth/Profile), `missions`, `user_missions`, `achievements`, `user_achievements`, `daily_rewards`.
- **Firestore-Integrated**: `user_stats`, `xp_transactions`, `coin_transactions`, `notifications`, `leaderboards`.
- **Hybrid**: Authentication remains strictly in SQLite due to PBKDF2 hashing limits (per `FIREBASE_MIGRATION.md`).

## Candidate Modules Considered

### Candidate 1: Daily Rewards (`daily_rewards`)
- **Dependency Complexity**: Low. Depends only on `RewardService` and `NotificationService` (both already support Firestore).
- **Firestore Cost**: Very low. Requires 1 read (or aggregation query) for `COUNT(*)` and 1 write per day per user.
- **Migration Complexity**: Low. Append-only ledger of claimed rewards.
- **Rollback Safety**: High. Safe to dual-write or rollback since it only affects a single isolated feature.
- **Testing Complexity**: Medium. Requires mocking dates to simulate 7-day cycles.
- **Browser QA Complexity**: Low. Simply clicking "Claim" on the dashboard.
- **Overall Risk**: Low.

### Candidate 2: Achievements (`achievements` & `user_achievements`)
- **Dependency Complexity**: Medium. Relies on the `AchievementRuleRegistry` which checks user stats.
- **Firestore Cost**: Medium. Requires reading all achievements and comparing with user progress.
- **Migration Complexity**: Medium. Requires migrating global static achievements and user-specific unlocked states.
- **Rollback Safety**: High. Unlocking achievements is append-only.
- **Testing Complexity**: High. Requires triggering various rules across the app.
- **Browser QA Complexity**: Medium. Requires manual testing of all triggers.
- **Overall Risk**: Medium.

### Candidate 3: Missions (`missions` & `user_missions`)
- **Dependency Complexity**: High. The core loop of the application. Touches stats, transactions, achievements, and UI heavily.
- **Firestore Cost**: High (Spark Plan risk). Potential N+1 queries if we fetch user assigned missions and then lookup global mission details individually.
- **Migration Complexity**: High. Relational mapping between global templates (`missions`) and user states (`user_missions`).
- **Rollback Safety**: Low. Reverting mission progress could cause state desync with `user_stats`.
- **Testing Complexity**: High.
- **Browser QA Complexity**: High.
- **Overall Risk**: High.

## Recommended Module: Daily Rewards
**Why it is safest**: We will migrate **Daily Rewards**. The prompt dictates we must not automatically choose a module just because it appears easy, but Daily Rewards is strategically the safest and most logical next step. It introduces the need for **aggregation/denormalization** (counting total claims to find the cycle day) which serves as a perfect low-risk proving ground for Firestore's aggregation queries or document incrementing before we tackle the complex relational joins required by Missions.

## Firestore Design (Daily Rewards)

### SQLite Schema Mapping
- **SQLite**: `daily_rewards` (id, user_id, day_number, reward_type, reward_value, claimed, claimed_at)
- **Firestore Subcollection**: `users/sqlite_{user_id}/daily_rewards/{auto_id}`
- **Firestore Document**:
  ```json
  {
    "day_number": 1,
    "reward_type": "xp",
    "reward_value": 50,
    "claimed_at": "SERVER_TIMESTAMP"
  }
  ```

### Read/Write Flow
1. **Read**: Fetch `total_claims` either via `COUNT(*)` aggregation on the subcollection, or by reading a new `total_daily_claims` counter on `user_stats`. Fetch the latest claim to check if today was claimed.
2. **Write**: Add a new document to the `daily_rewards` subcollection and increment `total_daily_claims` in `user_stats` (using a batched write).

### Feature Flag Design
- **Flag**: `FIRESTORE_DAILY_REWARDS_ENABLED` (in `config.py` and `.env`).
- **Logic**: If True, read/write to Firestore. If False, fallback to SQLite.

### Migration Strategy
- Create a migration script `scripts/migrate_daily_rewards.py`.
- Iterate over all users, fetch their SQLite `daily_rewards` where `claimed = 1`.
- Batch write these records into Firestore `users/sqlite_{user_id}/daily_rewards`.
- Update the user's `total_daily_claims` on their `user_stats` document.

### Rollback Strategy
- Switch `FIRESTORE_DAILY_REWARDS_ENABLED` to `False`. 
- Data created during Firestore usage won't automatically sync back to SQLite, so a reverse migration script will be prepared if needed, but since users only claim once a day, dual-writing is also an option for immediate safety.

### Spark-Plan Optimization
- Denormalize `total_daily_claims` onto the `user_stats` document. This avoids executing a `COUNT()` aggregation query (which costs 1 read per query) every time the dashboard loads.
- Dashboard load will only cost 1 read (fetching `user_stats` gets both the counter and stats), plus 1 read to check today's claim status.

### Security Considerations
- Ensure transactions are used when claiming so users cannot double-click and bypass the 1-per-day restriction.
- Backend verification of server local date (midnight reset) remains unchanged.

### Test Strategy
- Update `test_daily_rewards.py` to run parametrized tests against both SQLite and Firestore mock clients.
- Verify that `ValueError` is correctly raised on double claims in Firestore.

### Browser QA Strategy
- Verify the 7-day strip UI renders correctly.
- Verify clicking "Claim" updates XP/Coins instantly and triggers the notification.
- Verify reloading the dashboard shows "Claimed".

### Acceptance Criteria
- [ ] Feature flag `FIRESTORE_DAILY_REWARDS_ENABLED` controls data flow.
- [ ] Dashboard correctly calculates cycle day using Firestore data.
- [ ] Double-claiming is blocked.
- [ ] Existing SQLite tests pass.
- [ ] Firestore implementation achieves 100% test coverage.

## Known Risks
- Denormalization introduces a slight risk of `user_stats.total_daily_claims` getting out of sync with actual claim documents if a batched write fails.

## Open Decisions Requiring Approval
1. **Dual-Writing**: Should we dual-write to SQLite while `FIRESTORE_DAILY_REWARDS_ENABLED` is active to make rollbacks instant, or is strict separation preferred?
2. **Denormalization**: Do you approve adding `total_daily_claims` to `user_stats` to save read operations on the Spark plan?
