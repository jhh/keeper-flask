"""
Top level Flask app for Keeper.
"""
import os
from logging.config import dictConfig
import pandas as pd
from flask import Flask
from dash import Dash

app = Dash(__name__)
app.title = "Keeper"
server = app.server
server.config.from_object("keeper.default_settings")
server.config.from_envvar("KEEPER_SETTINGS")
app.config.suppress_callback_exceptions = True

LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "debug": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"},
        "production": {"format": "%(levelname)s in %(module)s: %(message)s"},
    },
    "handlers": {
        "debug": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "debug",
        },
        "production": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "production",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["debug" if server.config["DEBUG"] else "production"],
    },
}

dictConfig(LOG_CONFIG)

# pylint: disable=wrong-import-position
import keeper.db
import keeper.api
import keeper.index
