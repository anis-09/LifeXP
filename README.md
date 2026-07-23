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

## 🎮 Module 1 — Features Implemented

| Feature | Status |
|---------|--------|
| Landing Page (Hero, Features, How It Works, CTA, Footer) | ✅ |
| User Registration (Full Name, Email, Password, Confirm Password) | ✅ |
| Strong Password Validation (client + server) | ✅ |
| Password Hashing (pbkdf2:sha256) | ✅ |
| Duplicate Email Prevention | ✅ |
| User Login with Flask Session | ✅ |
| Logout | ✅ |
| Dashboard (Level, XP, Coins, Streak, Date) | ✅ |
| Real data from SQLite — no fake data | ✅ |
| Mobile-First Responsive Design | ✅ |
| Glassmorphism UI | ✅ |
| Poppins Font | ✅ |
| Smooth Animations | ✅ |
| SQL Injection Protection (parameterised queries) | ✅ |
| XSS Protection (Jinja2 auto-escaping) | ✅ |

---

## 🛡️ Security

- **Password hashing**: Werkzeug `pbkdf2:sha256` with 16-byte salt
- **SQL Injection**: All queries use parameterised placeholders (`?`)
- **XSS**: Jinja2 auto-escaping on all user data
- **Session security**: `HttpOnly`, `SameSite=Lax`, 7-day expiry
- **Input validation**: Both client-side (JS) and server-side (Python)

---

## 🎨 Design System

| Token | Value |
|-------|-------|
| Background | `#0a0a0f` |
| Brand Purple | `#7c3aed` |
| Brand Cyan | `#06b6d4` |
| Gold | `#f59e0b` |
| Font | Poppins (Google Fonts) |
| Border Radius | 16–24px (rounded cards) |
| Effect | Glassmorphism (`backdrop-filter: blur(20px)`) |

---

## 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Auto-generated | Flask session secret key |

For production, set `SECRET_KEY` as a persistent environment variable:

```bash
export SECRET_KEY="your-super-secret-key-here"
```

---

## 🧩 Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 + Flask |
| Database | SQLite (via sqlite3 stdlib) |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Templating | Jinja2 |
| Password Hashing | Werkzeug |

---

## 📋 Dependencies

```
Flask==3.0.3
Werkzeug==3.0.3
```

---

## 🗺️ Roadmap

> **Module 1** (current) — Landing, Register, Login, Dashboard
>
> Upcoming modules: Missions, Rewards, Profile, Leaderboard, AI Coach, Friends, Shop, Settings

---

*Built with ⚡ and ❤️ — LifeXP 2026*
