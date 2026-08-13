from flask import Blueprint, jsonify, session, request
from services.notification_service import NotificationService

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")

@notifications_bp.route("", methods=["GET"])
def get_unread():
    """
    Returns a list of unread notifications for the current user.
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    notifications = NotificationService.get_unread_for_user(session["user_id"])
    
    # query_db returns sqlite3.Row objects, convert to dict
    notifs_list = [dict(n) for n in notifications]
    
    return jsonify(notifs_list), 200

@notifications_bp.route("/read", methods=["PUT"])
def mark_read():
    """
    Marks a notification as read. If no ID is provided, marks all as read.
    """
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json() or {}
    notification_id = data.get("notification_id")
    
    success = NotificationService.mark_as_read(session["user_id"], notification_id)
    if success:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"error": "Failed to mark as read"}), 500
