# tests/conftest.py
import sys
import os
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from app import app as flask_app


@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    yield flask_app


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield