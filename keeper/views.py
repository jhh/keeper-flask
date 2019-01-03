from flask import render_template

from keeper import app
from keeper.db import get_db_cursor
import keeper.db


@app.route('/')
def index():
    app.logger.warning('sample message')
    with get_db_cursor() as cursor:
        cursor.execute("SELECT 1")
        app.logger.warn("SELECT RESULT = {}, cursor = {}".format(cursor.fetchone(), cursor))
    return render_template('index.html')
