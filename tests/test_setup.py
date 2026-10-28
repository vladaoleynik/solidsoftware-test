from flask import Flask
from flask.testing import FlaskClient


def test_app_is_configured_for_testing(app: Flask) -> None:
    assert app.config["TESTING"] is True


def test_client_fixture_is_available(client: FlaskClient) -> None:
    assert client is not None
