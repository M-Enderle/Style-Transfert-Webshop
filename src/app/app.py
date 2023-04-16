"""
Main application module for the app.
"""

import flask
from . import session, User

app = flask.Flask(__name__)


@app.route("/")
def index():
    """Index page."""
    return str(session.query(User).all())


if __name__ == "__main__":
    app.run()
