from flask import render_template, send_file
import pandas as pd

from keeper import app
from keeper.db import get_db_connection, get_db_cursor

from keeper.plots import motion_profile_plotdata
from keeper.models import MotionProfileAction


@app.route("/")
def index():
    app.logger.warning("sample message")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT count(*) FROM ACTIVITY")
        app.logger.warn(" activity count = {}".format(cursor.fetchone()[0]))
    return render_template("index.html.j2")


@app.route("/activities/")
def activities():
    return render_template("activities.html.j2")


ACTIONS_SQL = """
SELECT id, name, timestamp, meta->'type' as type, meta->'tags' as tags
FROM action
ORDER BY timestamp DESC
LIMIT 20
"""

@app.route("/actions/", methods=["GET"])
def actions():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return render_template("actions.html.j2", actions=cursor.fetchall())


@app.route("/actions/motion_profile/<action_id>", methods=["GET"])
def motion_profile(action_id):
    action = MotionProfileAction.by_id(action_id)
    return render_template("motion_profile.html.j2", action=action)


@app.route("/actions/test/<action_id>", methods=["GET"])
def test(action_id):
    return action_id


@app.route("/plots/motion_profile/<action_id>", methods=["GET"])
def motion_profile_plot(action_id):
    bytes_obj = motion_profile_plotdata(action_id)

    return send_file(bytes_obj, attachment_filename="plot.png", mimetype="image/png")
