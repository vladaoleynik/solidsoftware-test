from typing import TYPE_CHECKING

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

if TYPE_CHECKING:
    from typing import TypeAlias


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
migrate = Migrate()

# Flask-SQLAlchemy builds db.Model at runtime, which mypy cannot see.
if TYPE_CHECKING:
    Model: TypeAlias = Base  # noqa: UP040
else:
    Model = db.Model
