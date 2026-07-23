# LifeXP Database Architecture

Version: 1.0

---

# Purpose

This document defines the complete database architecture of LifeXP.

The goal is to build a scalable backend that supports:

- Authentication
- Missions
- XP
- Coins
- Achievements
- Daily Rewards
- Leaderboards
- Friends
- AI Coach
- Analytics

without requiring database redesign later.

---

# Architecture Rules

Never update XP directly.

Never update Coins directly.

All rewards must pass through transaction tables.

Routes must never communicate directly with the database.

Architecture

Route
↓

Service
↓

Model
↓

Database

---

# Database Engine

SQLite (Development)

Future

PostgreSQL

Database layer must remain database-independent.

---

# Tables

1.

users

2.

user_stats

3.

missions

4.

user_missions

5.

xp_transactions

6.

coin_transactions

7.

achievements

8.

user_achievements

9.

daily_rewards

10.

notifications

11.

settings

---

# users

Stores authentication data.

Columns

id

full_name

email

password_hash

avatar

created_at

last_login

is_active

Rules

Email must be unique.

Password must always be hashed.

Never store plain passwords.

---

# user_stats

Stores current player progress.

Columns

id

user_id

current_level

current_xp

current_coins

current_streak

longest_streak

missions_completed

missions_failed

last_updated

Rules

Only services can modify this table.

Never update directly from routes.

---

# missions

Stores every mission.

Columns

id

title

description

category

difficulty

xp_reward

coin_reward

is_daily

is_system

created_by

created_at

---

# user_missions

Mission progress.

Columns

id

user_id

mission_id

status

progress

assigned_at

completed_at

Status

Pending

In Progress

Completed

Skipped

Rules

One mission can only be completed once.

---

# xp_transactions

XP history.

Columns

id

user_id

source

reference_id

amount

created_at

Examples

Mission

Achievement

Daily Reward

Admin

Rules

Never delete rows.

Always append.

---

# coin_transactions

Coin history.

Columns

id

user_id

source

reference_id

amount

created_at

Rules

Append only.

---

# achievements

Master achievement list.

Columns

id

title

description

icon

xp_reward

coin_reward

---

# user_achievements

Stores unlocked achievements.

Columns

id

user_id

achievement_id

earned_at

---

# daily_rewards

Stores reward claims.

Columns

id

user_id

day_number

reward_type

reward_value

claimed

claimed_at

Rules

One claim per day.

---

# notifications

Stores notifications.

Columns

id

user_id

title

message

type

is_read

created_at

Types

Success

Warning

Achievement

Reward

LevelUp

Mission

---

# settings

User preferences.

Columns

id

user_id

theme

language

notifications_enabled

---

# Relationships

users

↓

user_stats

↓

user_missions

↓

missions

↓

xp_transactions

↓

coin_transactions

↓

user_achievements

↓

achievements

↓

daily_rewards

↓

notifications

↓

settings

---

# Services

auth_service

mission_service

xp_service

coin_service

achievement_service

notification_service

reward_service

stats_service

Rules

Business logic belongs here.

Routes should remain thin.

---

# Folder Structure

database/

schema.sql

seed.sql

db.py

migrations.py

models/

services/

routes/

---

# Indexes

Create indexes on

users.email

user_missions.user_id

xp_transactions.user_id

coin_transactions.user_id

notifications.user_id

---

# Security

Use parameterized SQL queries.

Never concatenate SQL strings.

Always validate input.

Never trust client-side values.

---

# Development Rules

Do not redesign tables unless necessary.

Always extend architecture instead of replacing it.

Maintain backward compatibility whenever possible.

All future modules must follow this document.