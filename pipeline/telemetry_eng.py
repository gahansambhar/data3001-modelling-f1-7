import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import logging
from .loading import read_process_line

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def telemetry_eng(df, line):
    # Compute turning window metrics.
    df = compute_turning_window(df)
    logger.info("Computed turning window metrics.")

    # Finding deviation from racing line at each point.
    df = racing_line_deviation(df, line)
    logger.info("Calculated deviation from racing line.")

    # Creates a combined brake–throttle feature for easier driver input analysis.
    df = brake_throttle(df)
    logger.info("Created combined brake–throttle variable.")

    # Calculates the angle between the front wheel direction and the car's facing direction.
    # Helps measure steering aggression and driver responsiveness.
    df = front_wheel_vs_car_direction(df)
    logger.info("Calculated front wheel vs car direction angle.")

    return df


def compute_turning_window(df):
    # Constants
    t1_apex = (375.57, 191.519)
    t2_apex = (368.93, 90)
    turn_radius = 50  # meters

    # Compute distance to each apex
    df["T1APEXDIST"] = np.sqrt(
        (df["WORLDPOSITIONX"] - t1_apex[0]) ** 2
        + (df["WORLDPOSITIONY"] - t1_apex[1]) ** 2
    )

    df["T2APEXDIST"] = np.sqrt(
        (df["WORLDPOSITIONX"] - t2_apex[0]) ** 2
        + (df["WORLDPOSITIONY"] - t2_apex[1]) ** 2
    )

    # Binary columns indicating if point is inside turning window
    df["T1WINDOW"] = df["T1APEXDIST"] <= turn_radius
    df["T2WINDOW"] = df["T2APEXDIST"] <= turn_radius

    return df


def racing_line_deviation(df, line):
    line_points = line[["WORLDPOSX", "WORLDPOSY"]].to_numpy()
    tree = cKDTree(line_points)

    driver_points = df[["WORLDPOSITIONX", "WORLDPOSITIONY"]].to_numpy()
    distances, _ = tree.query(driver_points)

    df["LINEDEVIATION"] = distances
    return df


def brake_throttle(df):
    """
    Creating a feature that combines the driver's throttle and brake input into
    one variable for convenient visualisation.
    """
    df["BRAKETHROTTLE"] = df["THROTTLE"] - df["BRAKE"]

    return df


def front_wheel_vs_car_direction(df):
    """
    Measures steering aggression and responsiveness.
    Calculates the angle between the **front wheel direction** and the **car's facing direction**.

    Interpretation:
    - Reflects the *steering input* directly.
    - Large angles → strong steering correction (possibly entering or exiting a turn).
    - Useful for measuring steering aggressiveness or response.
    """
    car_forward = np.stack([df["WORLDFORWARDDIRX"], df["WORLDFORWARDDIRY"]], axis=1)
    wheel_angle_rad = np.deg2rad(df["FRONTWHEELSANGLE"].values)

    # Rotate car forward vector by front wheel angle
    fw_x = car_forward[:, 0] * np.cos(wheel_angle_rad) - car_forward[:, 1] * np.sin(
        wheel_angle_rad
    )
    fw_y = car_forward[:, 0] * np.sin(wheel_angle_rad) + car_forward[:, 1] * np.cos(
        wheel_angle_rad
    )
    fw_vector = np.stack([fw_x, fw_y], axis=1)

    dot = np.einsum("ij,ij->i", fw_vector, car_forward)
    norm_fw = np.linalg.norm(fw_vector, axis=1)
    norm_forward = np.linalg.norm(car_forward, axis=1)
    cos_theta = np.clip(dot / (norm_fw * norm_forward), -1, 1)

    df["ANGLEFWVSCAR"] = np.rad2deg(np.arccos(cos_theta))

    # Small correction to keep everything within 0–90 range
    df["ANGLEFWVSCAR"] = np.where(
        df["ANGLEFWVSCAR"] > 90, 180 - df["ANGLEFWVSCAR"], df["ANGLEFWVSCAR"]
    )

    return df
