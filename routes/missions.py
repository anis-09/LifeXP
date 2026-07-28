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

    categories = MissionCategoryModel.get_all()

    if request.method == "POST":

        try:

            MissionService.create_mission(request.form)

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

            # DEBUG MODE
            # Show the actual error instead of hiding it.
            raise e

    return render_template(
        "create_mission.html",
        categories=categories
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