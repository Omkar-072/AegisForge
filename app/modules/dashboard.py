import os
from flask import Blueprint, send_from_directory

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/", methods=["GET"])
def index():
    """Serves the main visual schema designer."""
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    return send_from_directory(static_folder, "index.html")
    