import os
from flask import Flask
from logging.config import dictConfig

app = Flask(__name__)
app.config.from_object("keeper.default_settings")
app.config.from_envvar("KEEPER_SETTINGS")

log_config = {
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
        "handlers": ["debug" if app.config["DEBUG"] else "production"],
    },
}

dictConfig(log_config)

import keeper.db
import keeper.filters
import keeper.views
import keeper.api
