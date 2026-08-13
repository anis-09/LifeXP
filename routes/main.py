"""
routes/main.py
--------------
Blueprint for public-facing pages (landing).
"""

from flask import Blueprint, render_template, session, redirect, url_for

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))
    return render_template("landing.html")

@main_bp.route("/help")
def help_guide():
    return render_template("help.html")
