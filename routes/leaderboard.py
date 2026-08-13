"""
routes/leaderboard.py
---------------------
Blueprint for the leaderboard route.
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
)

from services.leaderboard_service import LeaderboardService
from models.user import get_user_by_id

leaderboard_bp = Blueprint("leaderboard", __name__)


@leaderboard_bp.route("/leaderboard")
def index():
    """
    Render authenticated leaderboard page.
    """

    if "user_id" not in session:
        from flask import flash
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    user = get_user_by_id(user_id)
    
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Valid periods: global, weekly, monthly, friends
    period = request.args.get("period", "global").lower()
    
    if period not in ["global", "weekly", "monthly", "friends"]:
        period = "global"

    leaderboard_data = LeaderboardService.get_leaderboard_data(user_id, period=period)

    return render_template(
        "leaderboard.html",
        user=user,
        **leaderboard_data
    )
