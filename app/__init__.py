from pathlib import Path

from flask import Flask

from app.config import Config
from app.extensions import db


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    with app.app_context():
        from app import models  # noqa: F401

        db.create_all()

    return app
