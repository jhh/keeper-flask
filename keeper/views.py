from flask import render_template

from keeper import app
from keeper.db import get_db_cursor
import keeper.db

@app.route('/')
def index():
    app.logger.warning('sample message')
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("SELECT count(*) FROM ACTIVITY")
        app.logger.warn(" activity count = {}".format(cursor.fetchone()[0]))
    return render_template('index.html.j2')

@app.route('/activities/')
def activities():
    return render_template('activities.html.j2')

ACTIONS_SQL = """
SELECT id, name, timestamp
FROM action
ORDER BY timestamp DESC
LIMIT 20
"""

@app.route('/actions/')
def actions():
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(ACTIONS_SQL)
        return render_template('actions.html.j2', actions=cursor.fetchall())


@app.template_filter('formatdatetime')
def format_datetime(value, format="%d %b %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)
