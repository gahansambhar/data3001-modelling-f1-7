import pandas as pd
from scipy.spatial import cKDTree
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def summary_eng(df):
    # Creates the summary dataframe containing lap-level statistics.
    summary = initialise_lap_summary(df)
    logger.info("Created summary dataframe.")

    # Calculates the average deviation from the racing line.
    summary = avg_line_distance(df, summary)
    logger.info("Calculated average distance to racing line.")

    # Calculates the minimum distances to either apex.
    summary = min_apex_distance(df, summary)
    logger.info("Calculated minimum distance to apex 1 and 2.")

    # Calculating average brake and throttle pressure.
    summary = add_avg_brake_pressure(df, summary)
    summary = add_avg_throttle_pressure(df, summary)
    logger.info("Calculated average brake and throttle pressure per lap.")

    # Calculating max brake and throttle pressure.
    summary = add_peak_brake_pressure(df, summary)
    summary = add_peak_throttle_pressure(df, summary)
    logger.info("Calculated peak brake and throttle pressure per lap.")

    # Calculating brake and turning points.
    summary = first_braking_point(df, summary)
    summary = first_turning_point(df, summary)
    logger.info("Braking and turning points calculated.")

    return summary


def initialise_lap_summary(df):
    """
    Create a summary dataframe per lap with lap index and sector_time.
    sector_time is computed as the difference between the first and last CURRENTLAPTIME in seconds.
    """
    rows = []

    for i in df["LAPINDEX"].unique():
        lap = df[df["LAPINDEX"] == i].sort_values("LAPDISTANCE", ascending=True)
        exit_speed = lap.iloc[-1]["SPEED"]
        rows.append({"LAPINDEX": i, "EXITSPEED": exit_speed})

    summary = pd.DataFrame(rows)
    return summary


def avg_line_distance(df, summary):
    """
    Calculate the average distance from the racing line per lap
    and add it to the summary dataframe.
    """
    avg_dist = df.groupby("LAPINDEX")["LINEDEVIATION"].mean().reset_index()
    avg_dist.rename(columns={"LINEDEVIATION": "AVGLINEDEVIATION"}, inplace=True)

    summary = summary.merge(avg_dist, on="LAPINDEX", how="left")
    return summary


def min_apex_distance(df, summary):
    p1 = (375.57, 191.519)
    p2 = (368.93, 90.0)
    rows = []
    for i in df["LAPINDEX"].unique():
        lap = df[df["LAPINDEX"] == i]
        lap_points = lap[["WORLDPOSITIONX", "WORLDPOSITIONY"]].to_numpy()
        tree = cKDTree(lap_points)
        distance1, _ = tree.query((p1[0], p1[1]))
        distance2, _ = tree.query((p2[0], p2[1]))
        rows.append((i, distance1, distance2))

    distances = pd.DataFrame(rows, columns=["LAPINDEX", "T1APEXDIST", "T2APEXDIST"])
    summary = pd.merge(summary, distances, on="LAPINDEX", how="inner")

    return summary


def add_avg_brake_pressure(df, summary):
    avg = df.groupby("LAPINDEX")["BRAKE"].mean().reset_index(name="AVGBRAKE")
    summary = summary.merge(avg, on="LAPINDEX", how="left")
    return summary


def add_avg_throttle_pressure(df, summary):
    avg = df.groupby("LAPINDEX")["THROTTLE"].mean().reset_index(name="AVGTHROTTLE")
    summary = summary.merge(avg, on="LAPINDEX", how="left")
    return summary


def add_peak_brake_pressure(df, summary):
    peak = df.groupby("LAPINDEX")["BRAKE"].max().reset_index(name="PEAKBRAKE")
    summary = summary.merge(peak, on="LAPINDEX", how="left")
    return summary


def add_peak_throttle_pressure(df, summary):
    peak = df.groupby("LAPINDEX")["THROTTLE"].max().reset_index(name="PEAKTHROTTLE")
    summary = summary.merge(peak, on="LAPINDEX", how="left")
    return summary


def first_braking_point(df, summary, brake_thresh=0.2):
    rows = []
    for i in df["LAPINDEX"].unique():
        lap = df[df["LAPINDEX"] == i]
        braking_points = lap[lap["BRAKE"] > brake_thresh]
        if not braking_points.empty:
            first_brake = braking_points.iloc[0]
            rows.append(
                (
                    i,
                    first_brake["WORLDPOSITIONX"],
                    first_brake["WORLDPOSITIONY"],
                    first_brake["BRAKE"],
                )
            )
        else:
            rows.append((i, None, None, 0))

    brake_df = pd.DataFrame(
        rows, columns=["LAPINDEX", "BRAKEX", "BRAKEY", "BRAKEPOINTPRESSURE"]
    )
    summary = pd.merge(summary, brake_df, on="LAPINDEX", how="left")
    return summary


def first_turning_point(df, summary, turn_thresh=0.2):
    rows = []
    for i in df["LAPINDEX"].unique():
        lap = df[df["LAPINDEX"] == i]
        turning_points = lap[lap["STEER"].abs() > turn_thresh]
        if not turning_points.empty:
            first_turn = turning_points.iloc[0]
            rows.append(
                (
                    i,
                    first_turn["WORLDPOSITIONX"],
                    first_turn["WORLDPOSITIONY"],
                    first_turn["STEER"],
                )
            )
        else:
            rows.append((i, None, None, 0))

    turn_df = pd.DataFrame(rows, columns=["LAPINDEX", "TURNX", "TURNY", "TURNANGLE"])
    summary = pd.merge(summary, turn_df, on="LAPINDEX", how="left")
    return summary
