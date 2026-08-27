import pandas as pd
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "tml-data"
HALF_LIFE_DAYS = 180
DATA_FILES = {
    "ATP": sorted(DATA_DIR.glob("[0-9][0-9][0-9][0-9].csv")),
    "WTA": sorted(DATA_DIR.glob("[0-9][0-9][0-9][0-9]_wta.csv")),
}

DEFAULTS_BY_TOUR = {
    "ATP": (0.60, 0.30),
    "WTA": (0.50, 0.40),
}

@lru_cache(maxsize=2)
def load_dataset(tour="ATP"):
    """Load and cache the combined 2025 and 2026 dataset for a tour."""
    try:
        data_files = DATA_FILES[tour.upper()]
    except KeyError as error:
        raise ValueError("tour must be either 'ATP' or 'WTA'") from error

    return pd.concat((pd.read_csv(data_file) for data_file in data_files), ignore_index=True)


def player_stats(df, player_name, surface="Hard", tour="ATP", as_of=None):
    """Return serve/return win percentages for a player on a surface."""
    default_serve_win, default_return_win = DEFAULTS_BY_TOUR[tour.upper()]
    as_of = pd.Timestamp.today().normalize() if as_of is None else pd.Timestamp(as_of)
    dated_df = df.copy()
    dated_df["tourney_date"] = pd.to_datetime(
        dated_df["tourney_date"].astype(str), format="%Y%m%d", errors="coerce"
    )
    surface_df = dated_df[
        (dated_df["surface"] == surface)
        & dated_df["tourney_date"].notna()
        & (dated_df["tourney_date"] <= as_of)
    ]
    winner_df = surface_df[surface_df["winner_name"] == player_name]
    loser_df = surface_df[surface_df["loser_name"] == player_name]

    if surface_df.shape[0] == 0 or (len(winner_df) == 0 and len(loser_df) == 0):
        return {
            "serve_pct": default_serve_win,
            "return_pct": default_return_win,
            "found": False,
        }

    winner_weights = 0.5 ** (
        (as_of - winner_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    loser_weights = 0.5 ** (
        (as_of - loser_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    weighted_sum = lambda values, weights: values.mul(weights).sum()

    svpts_won = (
        weighted_sum(winner_df["w_1stWon"], winner_weights)
        + weighted_sum(winner_df["w_2ndWon"], winner_weights)
        + weighted_sum(loser_df["l_1stWon"], loser_weights)
        + weighted_sum(loser_df["l_2ndWon"], loser_weights)
    )

    rtpts_won = (
        weighted_sum(winner_df["l_svpt"], winner_weights)
        - (
            weighted_sum(winner_df["l_1stWon"], winner_weights)
            + weighted_sum(winner_df["l_2ndWon"], winner_weights)
        )
        + weighted_sum(loser_df["w_svpt"], loser_weights)
        - (
            weighted_sum(loser_df["w_1stWon"], loser_weights)
            + weighted_sum(loser_df["w_2ndWon"], loser_weights)
        )
    )

    total_svpts = weighted_sum(winner_df["w_svpt"], winner_weights) + weighted_sum(
        loser_df["l_svpt"], loser_weights
    )
    total_rtpts = weighted_sum(winner_df["l_svpt"], winner_weights) + weighted_sum(
        loser_df["w_svpt"], loser_weights
    )

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
