# ⚡ LifeXP — Gamify Your Life

> Turn your daily habits and goals into an epic RPG adventure. Earn XP, level up, collect coins, and become the hero of your own story.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
# 1. Navigate to the project directory
cd LifeXP

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

### Open in Browser

```
http://localhost:5000
```

The SQLite database (`database.db`) is created automatically on first run.

---

## 📁 Project Structure

```
LifeXP/
├── app.py                  # Flask entry point & app factory
├── requirements.txt        # Python dependencies
├── database.db             # SQLite database (auto-created)
├── README.md               # This file
│
├── models/
│   ├── __init__.py
│   └── user.py             # User model — CRUD + password hashing
│
├── routes/
│   ├── __init__.py
│   ├── main.py             # Landing page blueprint
│   ├── auth.py             # Register / Login / Logout blueprint
│   └── dashboard.py        # Dashboard blueprint
│
├── services/
│   ├── __init__.py
│   └── auth_service.py     # Business logic — register & login
│
├── utils/
│   ├── __init__.py
│   ├── db.py               # SQLite connection helper & schema init
│   └── validators.py       # Input validation utilities
│
├── templates/
│   ├── base.html           # Shared Jinja2 base layout
│   ├── landing.html        # Public landing page
│   ├── register.html       # Registration form
│   ├── login.html          # Login form
│   └── dashboard.html      # Authenticated dashboard
│
└── static/
    ├── css/
    │   ├── variables.css   # Design tokens (colours, spacing, radii)
    │   ├── animations.css  # Keyframes & animation utility classes
    │   ├── base.css        # Reset, typography, shared components
    │   ├── landing.css     # Landing page styles
    │   ├── auth.css        # Register & Login styles
    │   └── dashboard.css   # Dashboard styles
    │
    └── js/
        ├── landing.js      # Landing page interactivity
        ├── auth.js         # Form validation & UX
        └── dashboard.js    # Dashboard animations & interactivity
```

---

## 🎮 Modules Implemented (v1.0)

LifeXP v1.0 includes the following core features:
- **Authentication**: Secure Login, Registration, Password Hashing.
- **Dashboard**: Real-time stats, current progress, active quests.
- **Missions**: Daily auto-refreshing tasks and one-time epic quests.
- **Rewards**: Earn XP and Coins, Daily Login Streaks.
- **Achievements**: Unlock badges for milestones (Level, XP, Streaks).
- **Leaderboard**: Compete globally and weekly with other heroes.
- **Profile**: Customize your premium RPG avatar and view history.
- **Notifications**: Real-time alerts for level-ups and milestones.
- **Nova AI Coach**: Rule-based deterministic coaching engine.
- **Production Ready**: Secured with strict HTTP headers and Waitress WSGI.

---

## 🗺️ Roadmap

> **Version 1.0** (Current) — Core Game Loop, Leaderboard, AI Coach
>
> Upcoming versions (v2.0+): Friends & Social, Premium Shop, Advanced Customization, Habit Tracking.

---

*Built with ⚡ and ❤️ — LifeXP 2026*
