from pathlib import Path

from app import create_app
from app.extensions import db

SEED_PATH = Path(__file__).resolve().parent.parent / "db" / "seed.sql"


def main() -> None:
    app = create_app()
    statements = [
        statement.strip()
        for statement in SEED_PATH.read_text().split(";")
        if statement.strip()
    ]
    with app.app_context(), db.engine.begin() as connection:
        for statement in statements:
            connection.exec_driver_sql(statement)


if __name__ == "__main__":
    main()
