"""
routes/dashboard.py
-------------------
Blueprint for the authenticated dashboard route.
"""

from flask import Blueprint, render_template, redirect, url_for, session
from models.user import get_user_by_id
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
def index():
    """Render dashboard. Requires authenticated session."""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = get_user_by_id(session['user_id'])
    if not user:
        # User deleted — clear stale session
        session.clear()
        return redirect(url_for('auth.login'))

    # Calculate XP progress to next level (100 XP per level)
    xp_needed = user['level'] * 100
    xp_progress = min(100, int((user['xp'] % xp_needed) / xp_needed * 100)) if xp_needed else 0

    today = datetime.now().strftime("%A, %B %d, %Y")

    return render_template(
        'dashboard.html',
        user=user,
        xp_progress=xp_progress,
        xp_needed=xp_needed,
        today=today
    )


@dashboard_bp.route('/')
def landing_redirect():
    """Root path — redirect to landing or dashboard."""
    return redirect(url_for('main.landing'))
