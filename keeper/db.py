"""
PostgreSQL connection management.
"""
from contextlib import contextmanager
from urllib.parse import urlparse
import click
from flask.cli import with_appcontext
from psycopg2.pool import ThreadedConnectionPool
from keeper import server

URL = urlparse(server.config["DB_URL"])
_pool = ThreadedConnectionPool(  # pylint: disable=invalid-name
    server.config["DB_MIN_CONN"],
    server.config["DB_MAX_CONN"],
    database=URL.path[1:],
    user=URL.username,
    password=URL.password,
    host=URL.hostname,
    port=URL.port,
)

server.logger.info("initialized pool: {}".format(_pool))


@contextmanager
def get_db_connection():
    try:
        connection = _pool.getconn()
        yield connection
    finally:
        _pool.putconn(connection)


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


def migrate_action_meta():
    with get_db_cursor(commit=True) as cursor1:
        cursor1.execute("SELECT id, data FROM action")
        for record in cursor1:
            with get_db_cursor(commit=True) as cursor2:
                cursor2.execute(
                    "UPDATE action SET meta = meta ||jsonb %s WHERE id = %s",
                    (
                        {
                            "profile_ticks": int(record[1][0]),
                            "actual_ticks": int(record[1][1]),
                        },
                        record[0],
                    ),
                )

    with get_db_cursor(commit=True) as cursor1:
        cursor1.execute("SELECT id, meta FROM action")
        for record in cursor1:
            record_id = record[0]
            meta = record[1]
            with get_db_cursor(commit=True) as cursor2:
                cursor2.execute(
                    "UPDATE action SET meta = %s WHERE id = %s",
                    (
                        {
                            "dt": int(meta["dt"]),
                            "t1": int(meta["t1"]),
                            "t2": int(meta["t2"]),
                            "k_p": float(meta["k_p"]),
                            "tags": meta["tags"],
                            "type": meta["type"],
                            "v_prog": int(meta["vProg"]),  # renamed
                            "yaw": float(meta["azimuth"]),  # renamed
                            "gyro_end": float(meta["gyroEnd"]),  # renamed
                            "gyro_start": float(meta["gyroStart"]),  # renamed
                            "direction": float(meta["direction"]),
                            "good_enough": int(meta["good_enough"]),
                            "actual_ticks": int(meta["actual_ticks"]),
                            "profile_ticks": int(meta["profile_ticks"]),
                        },
                        record_id,
                    ),
                )

    with get_db_cursor(commit=True) as cursor:
        cursor.execute("ALTER TABLE action DROP COLUMN measures")
        cursor.execute("ALTER TABLE action DROP COLUMN data")


@click.command("db-migrate")
@with_appcontext
def migrate_db_command():
    migrate_action_meta()
    click.echo("Migrated the database.")


server.cli.add_command(migrate_db_command)
