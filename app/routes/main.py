from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return jsonify({"status": "ok", "message": "Flask + SQLAlchemy is running"})
