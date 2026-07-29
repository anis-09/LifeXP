"""
routes/dashboard.py
-------------------
Blueprint for the authenticated dashboard route.
"""

from flask import Blueprint, render_template, redirect, url_for, session
from models.user import get_user_by_id
from models.user_stats import UserStatsModel
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

    # Fetch gameplay stats from user_stats table
    stats = UserStatsModel.get(session['user_id'])

    # Guard: if stats row is missing (legacy user), create it on the fly
    if not stats:
        UserStatsModel.create(session['user_id'])
        stats = UserStatsModel.get(session['user_id'])

    # Calculate XP progress to next level (1000 XP per level, matching XPService)
    XP_PER_LEVEL = 1000
    xp_needed = stats['current_level'] * XP_PER_LEVEL
    xp_progress = min(100, int((stats['current_xp'] % XP_PER_LEVEL) / XP_PER_LEVEL * 100)) if XP_PER_LEVEL else 0

    today = datetime.now().strftime("%A, %B %d, %Y")

    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        xp_progress=xp_progress,
        xp_needed=xp_needed,
        today=today
    )


@dashboard_bp.route('/')
def landing_redirect():
    """Root path — redirect to landing or dashboard."""
    return redirect(url_for('main.landing'))
