from flask import render_template, send_file

from keeper import app
from keeper.db import get_db_cursor

# import keeper.db
from keeper.plots import motion_plot


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
SELECT id, activity_id, name, timestamp, meta, measures, data
FROM action
WHERE id = %s
"""

TRACE_MAX_FORWARD_SQL = """
SELECT max(abs(value))
FROM action_trace
WHERE measure = 'forward' AND action_id = %s
"""

@app.route("/actions/", methods=["GET"])
def actions():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return render_template("actions.html.j2", actions=cursor.fetchall())


@app.route("/actions/motion_profile/<action_id>", methods=["GET"])
def motion_profile(action_id):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTION_DETAIL_SQL, (action_id,))
        results = cursor.fetchone()
        cursor.execute(TRACE_MAX_FORWARD_SQL, (action_id,))
        max_forward = cursor.fetchone()[0]

    app.logger.info("max forward = {}".format(max_forward))

    action = {
        'id': results[0],
        'activity_id': results[1],
        'name': results[2],
        'timestamp': results[3],
        'speed_profile': int(results[4]['vProg']) / 10,
        'direction': results[4]['direction'],
        'distance_profile': int(results[6][0]),
        'distance_actual': int(results[6][1]),
        'distance_error': int(results[6][0]) - int(results[6][1]),
        'gyro_start': float(results[4]['gyroStart']),
        'gyro_end': float(results[4]['gyroEnd']),
        'gyro_delta': float(results[4]['gyroEnd']) - float(results[4]['gyroStart']),
        'forward_max': max_forward,
    }

    return render_template("motion_profile.html.j2", action=action)


@app.route("/plots/motion_profile/<action_id>", methods=["GET"])
def motion_profile_plot(action_id):
    bytes_obj = motion_plot(action_id)

    return send_file(bytes_obj, attachment_filename="plot.png", mimetype="image/png")
