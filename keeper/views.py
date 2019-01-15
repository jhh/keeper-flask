from flask import render_template, send_file
import pandas as pd

from keeper import app
from keeper.db import get_db_connection, get_db_cursor

from keeper.plots import motion_profile_plotdata
from keeper.models import MotionProfile


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
SELECT id, name, timestamp
FROM action
ORDER BY timestamp DESC
LIMIT 20
"""

ACTION_DETAIL_SQL = """
SELECT id, activity_id, name, timestamp, meta
FROM action
WHERE id = %s
"""


@app.route("/actions/", methods=["GET"])
def actions():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return render_template("actions.html.j2", actions=cursor.fetchall())


@app.route("/actions/motion_profile/<action_id>", methods=["GET"])
def motion_profile(action_id):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(ACTION_DETAIL_SQL, (action_id,))
        record = cursor.fetchone()

        trace_df = pd.read_sql(
            "SELECT * FROM action_trace WHERE action_id = {}".format(action_id),
            con=connection,
        )
        connection.commit()

    trace_df = trace_df.pivot(index="millis", columns="measure", values="value")
    trace_df["vel_error"] = (
        trace_df["setpoint_vel"] / 10.0 - trace_df["actual_vel"].abs()
    )

    meta = record[4]
    action = MotionProfile(
        record[0],
        record[2],
        record[3],
        record[1],
        int(record[4]["v_prog"] / 10),
        meta["profile_ticks"],
        meta["direction"],
        meta["k_p"],
        meta["good_enough"],
        meta["actual_ticks"],
        trace_df["actual_vel"].abs().max(),
        trace_df["vel_error"].max(),
        meta["gyro_start"],
        meta["gyro_end"],
        trace_df["forward"].max(),
        trace_df["strafe"].max(),
        trace_df["yaw"].max(),
    )

    return render_template("motion_profile.html.j2", action=action)


@app.route("/plots/motion_profile/<action_id>", methods=["GET"])
def motion_profile_plot(action_id):
    bytes_obj = motion_profile_plotdata(action_id)

    return send_file(bytes_obj, attachment_filename="plot.png", mimetype="image/png")
