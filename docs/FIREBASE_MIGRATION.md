# Firebase Migration Status

## Overview
LifeXP is migrating its backend storage to Firebase (Firestore). However, the migration is strictly **data-only** at this time.

## 1. Firebase Auth Blocker
Firebase Authentication migration is currently **blocked**. 
- Existing SQLite users have password hashes stored in two formats: `scrypt` and `pbkdf2:sha256:600000`.
- The Firebase Admin Python SDK only supports PBKDF2 imports up to **120,000 rounds**.
- Since SQLite uses 600,000 rounds, those users cannot be seamlessly imported into Firebase Auth without compromising security or forcing password resets.

## 2. Authentication Source of Truth
**SQLite remains the absolute source of truth for authentication.**
- Login, registration, and password verification still use `database.db`.
- **No password hashes** are ever stored in Firestore.
- The migration script explicitly strips `password_hash` from user payloads.

## 3. Data-Only Firestore Migration
Firestore is being prepared as the data store for all LifeXP application data:
- `users` (profile only)
- `user_stats`
- `missions` and `user_missions`
- `xp_transactions` and `coin_transactions`
- `achievements` and `user_achievements`
- `daily_rewards`
- `notifications`

## 4. User ID Mapping
To link SQLite authentication with Firestore data, a deterministic mapping is used:
- SQLite `id` (e.g., `1`) translates to Firestore Document ID: `sqlite_1`.

## 5. Future Phases
Firebase Auth migration will be handled as a separate future phase. It may require a secure password-reset or re-authentication strategy to bypass the PBKDF2 round limitation.
