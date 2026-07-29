# CLAUDE.md

# LifeXP Development Guide

This document defines the development standards for the LifeXP project.

Claude must follow these rules for every task.

---

# Project Overview

LifeXP is a gamified life management application built with:

- Flask
- SQLite
- HTML
- CSS
- Vanilla JavaScript

Architecture:

Routes
↓

Services
↓

Models
↓

Database

Business logic belongs inside Services.

Database logic belongs inside Models.

Routes should remain thin.

---

# Core Architecture Rules

## Users Table

The users table stores ONLY authentication and profile data.

Allowed fields:

- id
- full_name
- email
- password_hash
- avatar
- created_at
- last_login
- is_active

Never store gameplay data inside users.

---

## User Stats Table

All gameplay information belongs inside user_stats.

Examples:

- current_level
- current_xp
- current_coins
- current_streak
- missions_completed

---

## XP Rules

XP rewards are handled only by XPService.

Do not update XP directly from routes.

Do not duplicate XP calculations.

XP_PER_LEVEL should come from a single shared constant.

---

## Coin Rules

Coin rewards are handled only by CoinService.

Never update coins directly inside routes.

---

## Mission Rules

Mission creation belongs in MissionService.

Mission completion belongs in MissionService.

Mission deletion must verify ownership before deleting.

Only the mission owner may edit or delete a mission.

---

# Authentication Rules

Passwords must always use Werkzeug password hashing.

Never store plain text passwords.

Always verify using password_hash.

Registration must automatically create a corresponding user_stats row.

Update last_login after successful login.

---

# Database Rules

Use parameterized SQL only.

Never concatenate SQL strings.

Never use SELECT * if only specific columns are required.

Always commit after INSERT, UPDATE, or DELETE.

---

# Route Rules

Routes should:

- Validate session
- Call services
- Flash messages
- Redirect or render templates

Routes should NOT contain business logic.

---

# Service Rules

Services should:

- Validate data
- Check permissions
- Handle business logic
- Raise ValueError for validation failures

Services should not render templates.

---

# Model Rules

Models should:

- Read/write the database
- Not contain business rules
- Not access Flask sessions

---

# Security Rules

Always validate ownership before:

- edit
- delete
- update

Never trust client input.

Always validate server-side.

---

# Coding Style

Follow existing project style.

Keep functions small.

Avoid duplicated code.

Prefer readable code over clever code.

Do not rewrite unrelated files.

Only modify files required for the task.

---

# File Output Rules

Always return COMPLETE updated files.

Never return snippets unless explicitly requested.

Preserve formatting.

Preserve comments when possible.

---

# Before Coding

Before making changes:

1. Inspect related files.
2. Understand existing architecture.
3. Minimize changes.
4. Preserve backward compatibility.

---

# After Coding

Always provide:

1. Files modified
2. Why each file changed
3. Testing checklist
4. Remaining issues
5. Suggested improvements (without implementing unless requested)

---

# Git Workflow

After successful testing:

git status

git add .

git commit -m "Meaningful commit message"

git push

---

# Preferred Development Workflow

Architecture discussion:
ChatGPT

Implementation:
Claude Agent

Review:
ChatGPT

Testing:
Developer

Git:
Developer

---

# Long-Term Goals

Maintain a production-quality codebase.

Keep architecture clean.

Avoid technical debt.

Optimize for maintainability, readability, and scalability.

Every change should improve the project without breaking existing functionality.