"""
Main application module for the app.
"""

import flask

from src.sts.app import database

session = database.session

app = flask.Flask(__name__)


@app.route("/test_db")
def test_db():
    """Test database connection."""
    try:
        database.session.query(database.User).all()
        return "Database connection successful."
    except Exception as error:  # pylint: disable=broad-except
        return f"Database connection failed: {error}"


@app.route("/")
def index():
    """Index page."""
    return "Hello, World!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
