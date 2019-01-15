from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class MotionProfile:
    """Class representing an Action."""

    id: int
    name: str
    timestamp: datetime
    activity_id: int
    profile_speed: int
    profile_distance: int
    profile_direction: float
    profile_k_p: float
    profile_good_enough: float
    actual_distance: int
    actual_speed_max: int
    speed_max_error: int
    gyro_start: float
    gyro_end: float
    swerve_forward_max: float
    swerve_strafe_max: float
    swerve_yaw_max: float
    distance_error: int = field(init=False)
    gyro_delta: float = field(init=False)

    def __post_init__(self):
        self.distance_error = self.profile_distance - self.actual_distance
        self.gyro_delta = self.gyro_end - self.gyro_start
