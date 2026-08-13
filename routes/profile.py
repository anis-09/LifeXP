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
    request,
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

@profile_bp.route("/edit", methods=["POST"])
def edit_profile():
    """Update user profile name and avatar."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
        
    full_name = request.form.get("full_name")
    avatar = request.form.get("avatar")
    
    try:
        ProfileService.update_user_profile(user_id, full_name, avatar)
        # Update session so the navbar reflects the new name immediately
        session["user_name"] = full_name.strip()
        session["user_avatar"] = avatar.strip()
        flash("Profile updated successfully!", "success")
    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash("An error occurred while updating profile.", "error")
        
    return redirect(url_for("profile.index"))
