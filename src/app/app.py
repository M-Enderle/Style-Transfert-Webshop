import flask

from . import load_user_toml, session

app = flask.Flask(__name__)


@app.route("/")
def index():
    return str(load_user_toml())


if __name__ == "__main__":
    app.run()
