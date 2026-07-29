"""
routes/dashboard.py
-------------------
Blueprint for the authenticated dashboard route.
"""

from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)

from models.user import get_user_by_id
from models.user_stats import UserStatsModel
from constants import XP_PER_LEVEL

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def index():
    """
    Render authenticated dashboard.
    """

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = get_user_by_id(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    stats = UserStatsModel.get(session["user_id"])

    if not stats:
        UserStatsModel.create(session["user_id"])
        stats = UserStatsModel.get(session["user_id"])

    current_level = stats["current_level"]
    current_xp = stats["current_xp"]

    level_start_xp = (current_level - 1) * XP_PER_LEVEL
    level_end_xp = current_level * XP_PER_LEVEL

    xp_into_level = current_xp - level_start_xp
    xp_required_this_level = level_end_xp - level_start_xp
    xp_remaining = max(level_end_xp - current_xp, 0)

    xp_progress = int(
        (xp_into_level / xp_required_this_level) * 100
    ) if xp_required_this_level else 0

    today = datetime.now().strftime("%A, %B %d, %Y")

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats,
        today=today,

        xp_progress=xp_progress,
        xp_into_level=xp_into_level,
        xp_required_this_level=xp_required_this_level,
        xp_remaining=xp_remaining,
        level_start_xp=level_start_xp,
        level_end_xp=level_end_xp,
    )


@dashboard_bp.route("/")
def landing_redirect():
    """
    Root path.
    """

    return redirect(
        url_for("main.landing")
    )