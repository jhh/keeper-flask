import json
import psycopg2
from psycopg2.extras import Json, execute_values
from flask import request
from keeper import app
from keeper.db import get_db_cursor

psycopg2.extensions.register_adapter(dict, Json)

ACTIVITY_SQL = """
INSERT INTO activity(id, name, meta, measures, data)
VALUES (%s, %s, %s, %s, %s)
"""

ACTION_SQL = """
INSERT INTO action(activity_id, name, meta, trace_measures)
VALUES (%s, %s, %s, %s)
RETURNING id
"""

TRACE_SQL = """
INSERT INTO trace(action_id, millis, data) VALUES %s
"""


@app.route("/activities", methods=["POST"])
def post_activity():
    doc = request.json
    # app.logger.debug(doc)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            ACTIVITY_SQL,
            (doc["id"], doc["name"], doc["meta"], doc["measures"], doc["data"]),
        )
    return "OK - {}".format(doc["id"])


@app.route("/actions", methods=["POST"])
def post_action():
    doc = request.json
    # json.dump(doc, sys.stdout, indent=4)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            ACTION_SQL,
            (
                doc["activity"],
                doc["name"],
                doc["meta"],
                doc["traceMeasures"],
            ),
        )

        action_id = cursor.fetchone()[0]

        values = [(action_id, data.pop(0), data) for data in doc["traceData"]]

        execute_values(
            cursor,
            TRACE_SQL,
            values,
            template="(%s, %s, %s)",
            page_size=500,
        )

    return "OK - {}".format(action_id)
