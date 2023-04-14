"""
Main application module for the app.
"""

import flask

app = flask.Flask(__name__)


@app.route("/")
def index():
    """ Index page. """
    return "Hello world!"


if __name__ == "__main__":
    app.run()
