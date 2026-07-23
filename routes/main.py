"""
routes/main.py
--------------
Blueprint for public-facing pages (landing).
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    """Render the public landing page."""
    return render_template('landing.html')
