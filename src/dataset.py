import pandas as pd
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "tml-data"
DATA_FILES = {
    "ATP": DATA_DIR / "2025.csv",
    "WTA": DATA_DIR / "2025_wta.csv",
}

DEFAULTS_BY_TOUR = {
    "ATP": (0.60, 0.30),
    "WTA": (0.50, 0.40),
}

@lru_cache(maxsize=2)
def load_dataset(tour="ATP"):
    """Load and cache the local 2025 dataset for a tour."""
    try:
        data_file = DATA_FILES[tour.upper()]
    except KeyError as error:
        raise ValueError("tour must be either 'ATP' or 'WTA'") from error

    return pd.read_csv(data_file)


def player_stats(df, player_name, surface="Hard", tour="ATP"):
    """Return serve/return win percentages for a player on a surface."""
    default_serve_win, default_return_win = DEFAULTS_BY_TOUR[tour.upper()]
    surface_df = df[df["surface"] == surface]
    winner_df = surface_df[surface_df["winner_name"] == player_name]
    loser_df = surface_df[surface_df["loser_name"] == player_name]

    if surface_df.shape[0] == 0 or (len(winner_df) == 0 and len(loser_df) == 0):
        return {
            "serve_pct": default_serve_win,
            "return_pct": default_return_win,
            "found": False,
        }

    svpts_won = (
        winner_df["w_1stWon"].sum()
        + winner_df["w_2ndWon"].sum()
        + loser_df["l_1stWon"].sum()
        + loser_df["l_2ndWon"].sum()
    )

    rtpts_won = (
        winner_df["l_svpt"].sum()
        - (winner_df["l_1stWon"].sum() + winner_df["l_2ndWon"].sum())
        + loser_df["w_svpt"].sum()
        - (loser_df["w_1stWon"].sum() + loser_df["w_2ndWon"].sum())
    )

    total_svpts = winner_df["w_svpt"].sum() + loser_df["l_svpt"].sum()
    total_rtpts = winner_df["l_svpt"].sum() + loser_df["w_svpt"].sum()

    if total_svpts == 0 or total_rtpts == 0:
        return {
            "serve_pct": default_serve_win,
            "return_pct": default_return_win,
            "found": False,
        }

    return {
        "serve_pct": svpts_won / total_svpts,
        "return_pct": rtpts_won / total_rtpts,
        "found": True,
    }
