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
    return render_template('index.html')
