import pandas as pd


def read_data(path=None):
    """Load the UNSW F1 2024 dataset, defaulting to repo structure if no path is given."""
    if path:
        return pd.read_csv(f"{path}")
    else:
        return pd.read_csv("data/F1CleanedFinal.csv")


def read_process_line(path=None):
    """Load and restrict the right track limits to expected coordinate bounds."""
    if path:
        line = pd.read_csv(f"{path}")
    else:
        line = pd.read_csv("data/f1sim-ref-line.csv")

    line = line.sort_values("FRAME")
    return line
