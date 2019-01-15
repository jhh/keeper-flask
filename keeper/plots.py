import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import io
import base64
from keeper.db import get_db_connection

matplotlib.use("Agg")


def motion_profile_plotdata(action_id):
    trace_df = None
    with get_db_connection() as connection:
        trace_df = pd.read_sql(
            "SELECT * FROM action_trace WHERE action_id = {}".format(action_id),
            con=connection,
        )
    vel_df = trace_df.pivot(index="millis", columns="measure", values="value")
    vel_df["actual_vel"] = vel_df["actual_vel"].abs()
    vel_df["setpoint_vel"] = vel_df["setpoint_vel"] / 10.0
    vel_df["profile_vel"] = vel_df["profile_vel"] / 10.0
    vel_df["ticks_error"] = vel_df["actual_ticks"] - vel_df["profile_ticks"]

    fig, (vel_ax, ticks_ax, gyro_ax) = plt.subplots(
        nrows=3, ncols=1, sharex=True, figsize=(10, 15)
    )
    vel_ax.set(title="Velocity", ylabel="ticks/100ms")
    ticks_ax.set(title="Distance Error", ylabel="ticks")
    gyro_ax.set(title="Gyro Angle", ylabel="degrees")
    vel_df[["profile_vel", "setpoint_vel", "actual_vel"]].plot(ax=vel_ax, grid=False)
    vel_df[["ticks_error"]].plot(ax=ticks_ax, grid=False, legend=False)
    vel_df[["gyro_angle"]].plot(ax=gyro_ax, grid=False, legend=False)

    bytes_image = io.BytesIO()
    fig.savefig(bytes_image, format="png")
    bytes_image.seek(0)
    return bytes_image
