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

    # User must be logged in
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

        except Exception as e:

            raise e

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

        MissionService.complete_mission(
            mission_id=mission_id,
            user_id=session["user_id"]
        )

        flash(
            "🎉 Mission completed successfully!",
            "success"
        )

    except ValueError as error:

        flash(
            str(error),
            "error"
        )

    except Exception as e:

        raise e

    return redirect(
        url_for("missions.index")
    )


@missions_bp.route("/delete/<int:mission_id>")
def delete(mission_id):
    """
    Delete a mission.
    """

    MissionService.delete_mission(
        mission_id
    )

    flash(
        "🗑️ Mission deleted successfully!",
        "success"
    )

    return redirect(
        url_for("missions.index")
    )