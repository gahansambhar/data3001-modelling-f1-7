import pandas as pd


def re_indexing(df):
    """Add a global 0-based lap index per unique session/lap combination."""

    # Drop duplicates to get unique session/lap pairs in order
    unique_laps = df[["SESSIONUID", "CURRENTLAPNUM"]].drop_duplicates()

    # Sort by session, then lap
    unique_laps = unique_laps.sort_values(["SESSIONUID", "CURRENTLAPNUM"])

    # Assign a global 0-based index
    unique_laps["LAPINDEX"] = range(len(unique_laps))

    # Map the LAPINDEX back to all rows in the original dataframe
    df = df.merge(unique_laps, on=["SESSIONUID", "CURRENTLAPNUM"], how="left")

    return df
