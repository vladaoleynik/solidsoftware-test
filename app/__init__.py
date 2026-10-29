from typing import Any

from flask import Flask

from app.config import Config
from app.extensions import db, migrate


def create_app(config: type[Config] | dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)

    if config is None:
        app.config.from_object(Config)
    elif isinstance(config, dict):
        app.config.update(config)
    else:
        app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main_bp, payments_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(payments_bp)

    # Ensure models are imported so metadata is registered with Alembic.
    from app import models  # noqa: F401

    return app
