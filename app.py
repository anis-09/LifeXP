"""
app.py
------
LifeXP Flask application entry point.
Registers blueprints, initialises the database, and starts the dev server.
"""

import os
import secrets
from datetime import timedelta

from flask import Flask

from database.db import (
    close_db,
    initialize_database,
)

from routes.main import main_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.missions import missions_bp
from routes.profile import profile_bp
from routes.rewards import rewards_bp
from routes.leaderboard import leaderboard_bp
from routes.notifications import notifications_bp


def create_app() -> Flask:
    """Application factory."""

    app = Flask(__name__)

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY",
        secrets.token_hex(32)
    )

    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # --------------------------------------------------
    # Database
    # --------------------------------------------------

    app.teardown_appcontext(close_db)

    # --------------------------------------------------
    # Blueprints
    # --------------------------------------------------

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(missions_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(rewards_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(notifications_bp)

    # --------------------------------------------------
    # Security Headers
    # --------------------------------------------------
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    @app.context_processor
    def inject_celebration_queue():
        from flask import session
        from models.achievement import AchievementModel
        queue_ids = session.pop("celebration_queue", [])
        achievements = []
        if queue_ids:
            for ach_id in queue_ids:
                ach = AchievementModel.get_by_id(ach_id)
                if ach:
                    achievements.append({
                        "id":          ach["id"],
                        "name":        ach["name"],
                        "description": ach["description"],
                        "icon":        ach.get("icon") or "🏅",
                        "badge_tier":  ach.get("badge_tier") or "bronze",
                        "xp_reward":   ach.get("xp_reward", 0),
                        "coin_reward": ach.get("coin_reward", 0),
                    })
        return dict(celebration_achievements=achievements)

    return app


# --------------------------------------------------
# Initialise database
# --------------------------------------------------

initialize_database()


if __name__ == "__main__":
    print("WARNING: This is a development server. For production, please run 'python wsgi.py'.")
    app = create_app()
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )