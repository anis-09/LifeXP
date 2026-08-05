"""
routes/profile.py
-----------------
Blueprint for the Player Profile page — Sprint 4.4

Single thin GET route: auth gate → ProfileService → render template.
All business logic lives in ProfileService.
"""

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)

from services.profile_service import ProfileService

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile")
def index():
    """
    Render the authenticated player profile page.
    """

    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    profile_data = ProfileService.get_profile_data(session["user_id"])

    if profile_data is None:
        session.clear()
        return redirect(url_for("auth.login"))

    return render_template("profile.html", **profile_data)
