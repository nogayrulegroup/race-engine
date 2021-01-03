# coding: utf-8

import logging
import logging.config

from flask import Flask, render_template
from flask_socketio import SocketIO, emit


logging.config.dictConfig(
    dict(
        version=1,
        formatters={
            "f": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
            }
        },
        handlers={
            "h": {
                "class": "logging.StreamHandler",
                "formatter": "f",
                "level": logging.DEBUG,
            }
        },
        root={"handlers": ["h"], "level": logging.DEBUG},
    )
)

logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode='gevent', cors_allowed_origins='*')


@app.route("/")
def index():
    return render_template("index.html")


@socketio.event
def ping():
    logger.info("ping")
    emit("pong")


def main():
    socketio.run(app)


if __name__ == "__main__":
    main()
