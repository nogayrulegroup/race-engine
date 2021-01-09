# coding: utf-8

import os
import sys
import logging
import logging.config

from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit

loglevel = os.environ.get("LOG_LEVEL", "DEBUG")


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
                "level": getattr(logging, loglevel.upper()),
            }
        },
        root={"handlers": ["h"], "level": logging.DEBUG},
    )
)

logger = logging.getLogger(__name__)


WORLD_SIZE = 100
PLAYERS = ["X", "Y"]
DIRECTS = {
    "left": -1,
    "right": 1,
}


def new_world():
    m = ["." for _ in range(WORLD_SIZE)]
    return {
        "map": m,
        "players": {
            PLAYERS[0]: {"a": PLAYERS[0], "c": None, "p": 0},
            PLAYERS[1]: {"a": PLAYERS[1], "c": None, "p": WORLD_SIZE - 1},
        },
    }


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")


def action(m, player):
    c = player["c"]
    p = player["p"]
    m[p] = "."
    if c and 0 <= (p + c) < WORLD_SIZE:
        p = player["p"] = p + c
    m[p] = player["a"]


def update_map(world):
    m = world["map"]
    p0 = world["players"]["X"]
    p1 = world["players"]["Y"]
    action(m, p0)
    action(m, p1)


def background(world):
    while True:
        update_map(world)
        logger.debug("push world map: %s", world["map"])
        socketio.emit("fresh map", {"data": "".join(world["map"])})
        socketio.sleep(0.5)


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on_error()
def error_handler(e):
    logger.error(e, exc_info=sys.exc_info())


@socketio.event
def ping():
    logger.info("ping")
    emit("pong")


@socketio.event
def move(message):
    player = message["player"]
    direct = DIRECTS[message["direct"]]

    world = session["one"]
    world["players"][player]["c"] = direct


@socketio.event
def my_event(message):
    emit("response", {"data": message["data"]})


@socketio.event
def startgaming():
    world = new_world()
    session["one"] = world
    socketio.start_background_task(background, world)
    emit("response", {"data": "Connected"})


def main():
    socketio.run(app)


if __name__ == "__main__":
    main()
