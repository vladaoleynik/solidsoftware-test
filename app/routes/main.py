from flask import Blueprint, Response, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.get("/health")
def health() -> Response:
    return jsonify({"status": "ok", "message": "Flask + SQLAlchemy is running"})
