"""
routes/rewards.py
-----------------
Daily Rewards Blueprint — Sprint 5

Routes:
    GET  /rewards              — Full rewards page
    GET  /api/rewards/status   — JSON: current reward status
    POST /api/rewards/claim    — JSON: claim today's reward

All business logic lives in DailyRewardService.
Routes stay thin: auth guard → service → response.
"""

from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
)

from services.daily_reward_service import DailyRewardService

rewards_bp = Blueprint("rewards", __name__)


# ------------------------------------------------------------------
# Page Route
# ------------------------------------------------------------------

@rewards_bp.route("/rewards")
def index():
    """
    Render the Daily Rewards page.
    Requires authentication.
    """
    if "user_id" not in session:
        flash("Please login first.", "error")
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    status = DailyRewardService.get_reward_status(user_id)
    recent_claims = DailyRewardService.get_recent_claims(user_id)

    return render_template(
        "rewards.html",
        status=status,
        recent_claims=recent_claims,
    )


# ------------------------------------------------------------------
# API: Status
# ------------------------------------------------------------------

@rewards_bp.route("/api/rewards/status")
def api_status():
    """
    Return today's reward status as JSON.
    Used by the dashboard card to poll state without a full reload.
    """
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    status = DailyRewardService.get_reward_status(session["user_id"])

    return jsonify({
        "success": True,
        "data": {
            "day_number":         status["day_number"],
            "reward_label":       status["reward"]["label"],
            "reward_icon":        status["reward"]["icon"],
            "reward_type":        status["reward"]["type"],
            "xp_value":           status["reward"]["xp_value"],
            "coin_value":         status["reward"]["coin_value"],
            "claimed":            status["claimed"],
            "claimed_at":         status["claimed_at"],
            "seconds_until_next": status["seconds_until_next"],
            "schedule":           status["schedule"],
        }
    })


# ------------------------------------------------------------------
# API: Claim
# ------------------------------------------------------------------

@rewards_bp.route("/api/rewards/claim", methods=["POST"])
def api_claim():
    """
    Claim today's daily reward.
    Returns JSON with reward details used by the frontend for animation.
    """
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    try:
        result = DailyRewardService.claim(session["user_id"])

        return jsonify({
            "success": True,
            "message": f"Daily reward claimed! {result['reward']['icon']} {result['reward']['label']}",
            "data": {
                "day_number":    result["day_number"],
                "reward_label":  result["reward"]["label"],
                "reward_icon":   result["reward"]["icon"],
                "reward_type":   result["reward"]["type"],
                "xp_granted":    result["xp_granted"],
                "coins_granted": result["coins_granted"],
            }
        }), 200

    except ValueError as err:
        return jsonify({"success": False, "message": str(err)}), 400

    except Exception:
        return jsonify({"success": False, "message": "Something went wrong. Please try again."}), 500
