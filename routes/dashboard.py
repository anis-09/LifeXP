"""
routes/dashboard.py
-------------------
Blueprint for the authenticated dashboard route.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
)

from services.dashboard_service import DashboardService
from services.notification_service import NotificationService

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def index():
    """
    Render authenticated dashboard.
    """

    if "user_id" not in session:
        from flask import flash
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    dashboard_data = DashboardService.get_dashboard_data(
        session["user_id"]
    )

    if dashboard_data is None:
        session.clear()
        return redirect(url_for("auth.login"))

    # Trigger a mission reminder if applicable
    NotificationService.create_mission_reminder_if_needed(session["user_id"])

    return render_template(
        "dashboard.html",
        **dashboard_data
    )


@dashboard_bp.route("/")
def landing_redirect():
    """
    Root path.
    """

    return redirect(
        url_for("main.landing")
    )