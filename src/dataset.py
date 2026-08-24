import pandas as pd
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "tml-data"
DATA_FILES = {
    "ATP": DATA_DIR / "2025.csv",
    "WTA": DATA_DIR / "2025_wta.csv",
}
DEFAULT_SERVE_WIN = 0.60
DEFAULT_RETURN_WIN = 0.30

@lru_cache(maxsize=2)
def load_dataset(tour="ATP"):
    """Load and cache the local 2025 dataset for a tour."""
    try:
        data_file = DATA_FILES[tour.upper()]
    except KeyError as error:
        raise ValueError("tour must be either 'ATP' or 'WTA'") from error

    return pd.read_csv(data_file)


def player_stats(df, player_name, surface="Hard"):
    """Return serve/return win percentages for a player on a surface."""
    surface_df = df[df["surface"] == surface]
    winner_df = surface_df[surface_df["winner_name"] == player_name]
    loser_df = surface_df[surface_df["loser_name"] == player_name]

    if surface_df.shape[0] == 0 or (len(winner_df) == 0 and len(loser_df) == 0):
        return {
            "serve_pct": DEFAULT_SERVE_WIN,
            "return_pct": DEFAULT_RETURN_WIN,
            "found": False,
        }

    svpts_won = (
        winner_df["w_1stWon"].sum()
        + winner_df["w_2ndWon"].sum()
        + loser_df["w_1stWon"].sum()
        + loser_df["w_2ndWon"].sum()
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
            "serve_pct": DEFAULT_SERVE_WIN,
            "return_pct": DEFAULT_RETURN_WIN,
            "found": False,
        }

    return {
        "serve_pct": svpts_won / total_svpts,
        "return_pct": rtpts_won / total_rtpts,
        "found": True,
    }
