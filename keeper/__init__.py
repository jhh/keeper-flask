import os
from flask import Flask

app = Flask(__name__)
app.config.from_object("keeper.default_settings")
app.config.from_envvar("KEEPER_SETTINGS")

if not app.debug:
    import logging
    from logging.handlers import TimedRotatingFileHandler

    # https://docs.python.org/3.6/library/logging.handlers.html#timedrotatingfilehandler
    file_handler = TimedRotatingFileHandler(
        os.path.join(app.config["LOG_DIR"], "keeper.log"), "midnight"
    )
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(
        logging.Formatter("<%(levelname)s> %(message)s")
    )
    app.logger.addHandler(file_handler)

import keeper.db
import keeper.views
import keeper.api
