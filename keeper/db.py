import click
from contextlib import contextmanager
from flask import current_app
from flask.cli import with_appcontext
from psycopg2.pool import ThreadedConnectionPool
from urllib.parse import urlparse
from keeper import app

url = urlparse(app.config["DB_URL"])
pool = ThreadedConnectionPool(
    app.config["DB_MIN_CONN"],
    app.config["DB_MAX_CONN"],
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
)

app.logger.info("initialized pool: {}".format(pool))


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

def init_db():
    with current_app.open_resource('schema.sql') as schema:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(schema.read())

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

app.cli.add_command(init_db_command)