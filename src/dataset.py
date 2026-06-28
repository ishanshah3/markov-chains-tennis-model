import pandas as pd
from functools import lru_cache

DATA_URL = "https://raw.githubusercontent.com/Tennismylife/TML-Database/refs/heads/master/2025.csv"
DEFAULT_SERVE_WIN = 0.60
DEFAULT_RETURN_WIN = 0.30

@lru_cache(maxsize=1)
def load_dataset():
    """Load the tennis dataset and cache it for the session."""
    return pd.read_csv(DATA_URL)


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
