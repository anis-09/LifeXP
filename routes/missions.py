"""
routes/missions.py
------------------
Mission Routes
"""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)

from models.mission_category import MissionCategoryModel
from services.mission_service import MissionService

missions_bp = Blueprint(
    "missions",
    __name__,
    url_prefix="/missions"
)


@missions_bp.route("/")
def index():
    """
    Display all missions.
    """

    missions = MissionService.get_all_missions()

    return render_template(
        "missions.html",
        missions=missions
    )


@missions_bp.route("/create", methods=["GET", "POST"])
def create():
    """
    Create a new mission.
    """

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    categories = MissionCategoryModel.get_all()

    if request.method == "POST":

        try:

            MissionService.create_mission(
                data=request.form,
                user_id=session["user_id"]
            )

            flash(
                "🎉 Mission created successfully!",
                "success"
            )

            return redirect(
                url_for("missions.index")
            )

        except ValueError as error:

            flash(
                str(error),
                "error"
            )

        except Exception:
            raise

    return render_template(
        "create_mission.html",
        categories=categories
    )


@missions_bp.route("/complete/<int:mission_id>")
def complete(mission_id):
    """
    Mark a mission as completed.
    """

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    try:

        _mission, reward = MissionService.complete_mission(
            mission_id=mission_id,
            user_id=session["user_id"]
        )

        # Build a context-aware success message.
        parts = [
            f"🎉 Mission completed!  "
            f"⚡ +{reward['xp']} XP  "
            f"💰 +{reward['coins']} Coins  "
            f"🔥 Streak: {reward['streak']} day(s)"
        ]

        if reward.get("streak_milestone"):
            parts.append(
                f"  🏆 {reward['streak_milestone']}-Day Streak Bonus! "
                f"+{reward['bonus_xp']} XP  +{reward['bonus_coins']} Coins"
            )

        if reward.get("level_up"):
            parts.append(f"  ⭐ Level Up! You are now Level {reward['level']}!")

        flash("".join(parts), "success")

        # Store newly unlocked achievements in session for celebration modal.
        # Only keep fields the JS needs — avoids bloating the cookie.
        newly_unlocked = reward.get("newly_unlocked_achievements", [])
        if newly_unlocked:
            session["celebration_queue"] = [ach["id"] for ach in newly_unlocked]

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

    except Exception:
        raise

    return redirect(
        url_for("dashboard.index")
    )



@missions_bp.route("/delete/<int:mission_id>")
def delete(mission_id):
    """
    Delete a mission.
    """

    if "user_id" not in session:

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("auth.login")
        )

    try:

        MissionService.delete_mission(
            mission_id=mission_id,
            user_id=session["user_id"]
        )

        flash(
            "🗑️ Mission deleted successfully!",
            "success"
        )

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

    except Exception:
        raise

    return redirect(
        url_for("missions.index")
    )