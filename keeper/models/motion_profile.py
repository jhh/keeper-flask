import pandas as pd
from keeper.db import get_db_connection
from . import Action


class MotionProfileAction(Action):
    """Class representing an Motion Profile Action."""

    def __init__(
        self,
        profile_speed,
        profile_distance,
        profile_direction,
        profile_k_p,
        profile_good_enough,
        actual_distance,
        actual_speed_max,
        speed_max_error,
        gyro_start,
        gyro_end,
        swerve_forward_max,
        swerve_strafe_max,
        swerve_yaw_max,
        **kwargs,
    ):
        self.profile_speed = profile_speed
        self.profile_distance = profile_distance
        self.profile_direction = profile_direction
        self.profile_k_p = profile_k_p
        self.profile_good_enough = profile_good_enough
        self.actual_distance = actual_distance
        self.actual_speed_max = actual_speed_max
        self.speed_max_error = speed_max_error
        self.gyro_start = gyro_start
        self.gyro_end = gyro_end
        self.swerve_forward_max = swerve_forward_max
        self.swerve_strafe_max = swerve_strafe_max
        self.swerve_yaw_max = swerve_yaw_max
        self.distance_error = self.profile_distance - self.actual_distance
        self.gyro_delta = self.gyro_end - self.gyro_start
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            # f"{super().__repr__()} "
            f"MotionProfileAction(profile_speed={self.profile_speed}, "
            f"profile_distance={self.profile_distance}, profile_direction={self.profile_direction}"
            f"profile_k_p={self.profile_k_p}, profile_good_enough={self.profile_good_enough}"
            f"actual_distance={self.actual_distance}, actual_speed_max={self.actual_speed_max}"
            f")"
        )

    @staticmethod
    def by_id(action_id):
        with get_db_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, activity_id, name, timestamp, meta FROM action WHERE id = %s",
                (action_id,),
            )
            record = cursor.fetchone()

            trace_df = pd.read_sql(
                f"SELECT * FROM action_trace WHERE action_id = {action_id}",
                con=connection,
            )

        trace_df = trace_df.pivot(index="millis", columns="measure", values="value")
        trace_df["vel_error"] = (
            trace_df["setpoint_vel"] / 10.0 - trace_df["actual_vel"].abs()
        )

        meta = record[4]
        return MotionProfileAction(
            id=record[0],
            name=record[2],
            timestamp=record[3],
            tags=meta["tags"],
            activity_id=record[1],
            profile_speed=int(record[4]["v_prog"] / 10),
            profile_distance=meta["profile_ticks"],
            profile_direction=meta["direction"],
            profile_k_p=meta["k_p"],
            profile_good_enough=meta["good_enough"],
            actual_distance=meta["actual_ticks"],
            actual_speed_max=trace_df["actual_vel"].abs().max(),
            speed_max_error=trace_df["vel_error"].max(),
            gyro_start=meta["gyro_start"],
            gyro_end=meta["gyro_end"],
            swerve_forward_max=trace_df["forward"].max(),
            swerve_strafe_max=trace_df["strafe"].max(),
            swerve_yaw_max=trace_df["yaw"].max(),
        )
