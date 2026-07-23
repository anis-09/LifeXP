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

from utils.db import close_db, init_db
from routes.main import main_bp
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp


def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    # Configuration
    # ------------------------------------------------------------------ #
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # ------------------------------------------------------------------ #
    # Database teardown
    # ------------------------------------------------------------------ #
    app.teardown_appcontext(close_db)

    # ------------------------------------------------------------------ #
    # Blueprints
    # ------------------------------------------------------------------ #
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    return app


# Initialise database tables on first run
init_db()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
