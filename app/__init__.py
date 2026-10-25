from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # Ensure models are imported so metadata is registered with Alembic.
    from app import models  # noqa: F401

    return app
