import pandas as pd
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "tml-data"
HALF_LIFE_DAYS = 180
DATA_FILES = {
    "ATP": sorted(DATA_DIR.glob("[0-9][0-9][0-9][0-9].csv")),
    "WTA": sorted(DATA_DIR.glob("[0-9][0-9][0-9][0-9]_wta.csv")),
}

@lru_cache(maxsize=2)
def load_dataset(tour="ATP"):
    """Load and cache the combined 2025 and 2026 dataset for a tour."""
    try:
        data_files = DATA_FILES[tour.upper()]
    except KeyError as error:
        raise ValueError("tour must be either 'ATP' or 'WTA'") from error

    return pd.concat((pd.read_csv(data_file) for data_file in data_files), ignore_index=True)


def _average_rates(df):
    """Calculate aggregate serve and return win rates from match point totals."""
    numeric_df = df.copy()

    def valid_rows(frame, prefix):
        columns = [f"{prefix}_svpt", f"{prefix}_1stWon", f"{prefix}_2ndWon"]
        stats = frame[columns].apply(pd.to_numeric, errors="coerce")
        return stats.notna().all(axis=1) & stats.ge(0).all(axis=1) & (
            stats[f"{prefix}_1stWon"] + stats[f"{prefix}_2ndWon"]
            <= stats[f"{prefix}_svpt"]
        )

    for prefix in ("w", "l"):
        columns = [f"{prefix}_svpt", f"{prefix}_1stWon", f"{prefix}_2ndWon"]
        numeric_df[columns] = numeric_df[columns].apply(pd.to_numeric, errors="coerce")

    winner_serve_df = numeric_df[valid_rows(numeric_df, "w")]
    loser_serve_df = numeric_df[valid_rows(numeric_df, "l")]
    winner_return_df = numeric_df[valid_rows(numeric_df, "l")]
    loser_return_df = numeric_df[valid_rows(numeric_df, "w")]

    serve_total = winner_serve_df["w_svpt"].sum() + loser_serve_df["l_svpt"].sum()
    serve_won = (
        winner_serve_df["w_1stWon"].sum()
        + winner_serve_df["w_2ndWon"].sum()
        + loser_serve_df["l_1stWon"].sum()
        + loser_serve_df["l_2ndWon"].sum()
    )
    return_total = winner_return_df["l_svpt"].sum() + loser_return_df["w_svpt"].sum()
    return_won = (
        winner_return_df["l_svpt"].sum()
        - winner_return_df["l_1stWon"].sum()
        - winner_return_df["l_2ndWon"].sum()
        + loser_return_df["w_svpt"].sum()
        - loser_return_df["w_1stWon"].sum()
        - loser_return_df["w_2ndWon"].sum()
    )

    if serve_total == 0 or return_total == 0:
        return None

    return serve_won / serve_total, return_won / return_total


def player_stats(df, player_name, surface="Hard", tour="ATP", as_of=None):
    """Return serve/return win percentages for a player on a surface."""
    tour = tour.upper()
    if tour not in DATA_FILES:
        raise ValueError("tour must be either 'ATP' or 'WTA'")
    as_of = pd.Timestamp.today().normalize() if as_of is None else pd.Timestamp(as_of)
    dated_df = df.copy()
    dated_df["tourney_date"] = pd.to_datetime(
        dated_df["tourney_date"].astype(str), format="%Y%m%d", errors="coerce"
    )
    eligible_df = dated_df[
        dated_df["tourney_date"].notna() & (dated_df["tourney_date"] <= as_of)
    ]
    surface_df = eligible_df[eligible_df["surface"] == surface]
    defaults = _average_rates(surface_df) or _average_rates(eligible_df) or (0.5, 0.5)
    default_serve_win, default_return_win = defaults
    winner_df = surface_df[surface_df["winner_name"] == player_name]
    loser_df = surface_df[surface_df["loser_name"] == player_name]

    def valid_serve_rows(frame, prefix):
        columns = [f"{prefix}_svpt", f"{prefix}_1stWon", f"{prefix}_2ndWon"]
        stats = frame[columns].apply(pd.to_numeric, errors="coerce")
        return stats.notna().all(axis=1) & stats.ge(0).all(axis=1) & (
            stats[f"{prefix}_1stWon"] + stats[f"{prefix}_2ndWon"]
            <= stats[f"{prefix}_svpt"]
        )

    valid_winner_stats = valid_serve_rows(winner_df, "w")
    valid_loser_stats = valid_serve_rows(loser_df, "l")
    winner_serve_df = winner_df[valid_winner_stats]
    loser_serve_df = loser_df[valid_loser_stats]
    winner_return_df = winner_df[valid_serve_rows(winner_df, "l")]
    loser_return_df = loser_df[valid_serve_rows(loser_df, "w")]

    if surface_df.shape[0] == 0 or (
        len(winner_serve_df) == 0
        and len(loser_serve_df) == 0
        and len(winner_return_df) == 0
        and len(loser_return_df) == 0
    ):
        return {
            "serve_pct": default_serve_win,
            "return_pct": default_return_win,
            "found": False,
        }

    winner_serve_weights = 0.5 ** (
        (as_of - winner_serve_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    loser_serve_weights = 0.5 ** (
        (as_of - loser_serve_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    winner_return_weights = 0.5 ** (
        (as_of - winner_return_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    loser_return_weights = 0.5 ** (
        (as_of - loser_return_df["tourney_date"]).dt.days / HALF_LIFE_DAYS
    )
    weighted_sum = lambda values, weights: values.mul(weights).sum()

    svpts_won = (
        weighted_sum(winner_serve_df["w_1stWon"], winner_serve_weights)
        + weighted_sum(winner_serve_df["w_2ndWon"], winner_serve_weights)
        + weighted_sum(loser_serve_df["l_1stWon"], loser_serve_weights)
        + weighted_sum(loser_serve_df["l_2ndWon"], loser_serve_weights)
    )

    rtpts_won = (
        weighted_sum(winner_return_df["l_svpt"], winner_return_weights)
        - (
            weighted_sum(winner_return_df["l_1stWon"], winner_return_weights)
            + weighted_sum(winner_return_df["l_2ndWon"], winner_return_weights)
        )
        + weighted_sum(loser_return_df["w_svpt"], loser_return_weights)
        - (
            weighted_sum(loser_return_df["w_1stWon"], loser_return_weights)
            + weighted_sum(loser_return_df["w_2ndWon"], loser_return_weights)
        )
    )

    total_svpts = weighted_sum(
        winner_serve_df["w_svpt"], winner_serve_weights
    ) + weighted_sum(
        loser_serve_df["l_svpt"], loser_serve_weights
    )
    total_rtpts = weighted_sum(
        winner_return_df["l_svpt"], winner_return_weights
    ) + weighted_sum(
        loser_return_df["w_svpt"], loser_return_weights
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
