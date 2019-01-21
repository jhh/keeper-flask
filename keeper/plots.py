import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import io
import base64
from keeper.db import get_db_connection

matplotlib.use("Agg")

grid = False


def motion_profile_plotdata(action_id):
    trace_df = None
    with get_db_connection() as connection:
        trace_df = pd.read_sql(
            "SELECT * FROM action_trace WHERE action_id = {}".format(action_id),
            con=connection,
        )
    vel_df = trace_df.pivot(index="millis", columns="measure", values="value")
    if vel_df.actual_vel.mean() < 0:
        vel_df.actual_vel = vel_df.actual_vel * -1
    vel_df.setpoint_vel = vel_df.setpoint_vel / 10.0
    vel_df.profile_vel = vel_df.profile_vel / 10.0
    vel_df["ticks_error"] = vel_df.actual_ticks - vel_df.profile_ticks

    fig, (vel_ax, ticks_ax) = plt.subplots(
        nrows=2, ncols=1, sharex=True, figsize=(12, 12)
    )
    vel_ax.set(title="Velocity and Current", ylabel="ticks/100ms")
    ticks_ax.set(title="Gyro and Distance Error", ylabel="ticks")
    vel_df[["profile_vel", "setpoint_vel", "actual_vel"]].plot(ax=vel_ax, grid=grid)

    if 'drive_current' in vel_df.columns:
        i_ax = vel_ax.twinx()
        vel_df.drive_current.plot(ax=i_ax, color="r")
        i_ax.set_ylabel("current", color="r")
        i_ax.tick_params("y", colors="r")

    gyro_ax = ticks_ax.twinx()
    vel_df.ticks_error.plot(ax=ticks_ax, grid=grid, legend=False)
    vel_df.gyro_angle.plot(ax=gyro_ax, grid=grid, color="r")
    gyro_ax.set_ylabel("gyro angle", color="r")
    gyro_ax.tick_params("y", colors="r")

    bytes_image = io.BytesIO()
    fig.savefig(bytes_image, format="png")
    plt.close(fig)
    bytes_image.seek(0)
    return bytes_image
