# LifeXP Coding Standards

Version: 1.0

---

# Purpose

This document defines the coding standards used throughout the LifeXP project.

All developers and AI tools must follow these rules to keep the codebase clean, consistent, and maintainable.

---

# General Principles

- Write clean and readable code.
- Prefer simplicity over cleverness.
- Avoid duplicate code (DRY principle).
- Keep functions small and focused.
- Separate presentation, business logic, and data access.

---

# Project Structure

```
LifeXP/

database/
models/
routes/
services/
static/
templates/
utils/
tests/
docs/
```

Each folder has a single responsibility.

---

# Python Standards

Follow PEP 8.

Use snake_case for:

- variables
- functions
- file names

Example

```python
def complete_mission():
    pass
```

Use PascalCase for classes.

```python
class MissionService:
    pass
```

Constants must be uppercase.

```python
MAX_LEVEL = 100
```

---

# Function Rules

Each function should perform only one task.

Good

```python
calculate_xp()
```

Bad

```python
calculate_xp_and_send_email_and_update_database()
```

---

# Routes

Routes should only:

- receive request
- validate input
- call service
- return response

Never place business logic inside routes.

Correct

```
Route

↓

Mission Service

↓

Database
```

---

# Services

All business logic belongs inside services.

Examples

- XP calculation
- Coin rewards
- Achievement unlocking
- Notifications
- Streak updates

---

# Database

Never concatenate SQL strings.

Always use parameterized queries.

Good

```python
cursor.execute(
    "SELECT * FROM users WHERE email=?",
    (email,)
)
```

---

# HTML Standards

Use semantic HTML.

Preferred tags

- header
- nav
- main
- section
- article
- footer

Avoid unnecessary div nesting.

---

# CSS Standards

Use CSS variables.

Example

```css
:root{
    --primary:#4F46E5;
    --background:#0F172A;
}
```

No inline CSS.

Use reusable classes.

---

# JavaScript Standards

Use modern ES6+ syntax.

Prefer

- const
- let
- arrow functions
- modules

Avoid global variables.

---

# Naming Conventions

Variables

```
user_name
```

Functions

```
calculate_level()
```

Classes

```
MissionService
```

Files

```
mission_service.py
```

---

# Comments

Write comments only when necessary.

Bad

```python
x = x + 1
```

Good

```python
# Calculate streak after mission completion.
```

---

# Error Handling

Always catch expected exceptions.

Return meaningful error messages.

Never expose internal server errors to users.

---

# Logging

Log

- authentication
- mission completion
- errors
- rewards

Do not log passwords.

---

# Git Standards

Commit after every completed feature.

Good commit messages

```
Add mission completion logic

Fix dashboard refresh bug

Implement XP transaction system
```

Bad

```
update

fix

done
```

---

# Code Review Checklist

Before every commit:

- Code runs successfully.
- No duplicate logic.
- No hardcoded secrets.
- Proper validation.
- Proper error handling.
- Clean formatting.
- Meaningful names.
- Documentation updated if needed.

---

# Golden Rule

Readable code is better than clever code.

Every file should be understandable by a new developer within a few minutes.