import re
import unicodedata
from datetime import date
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "tml-data"
CURRENT_YEAR = date.today().year
DATA_FILES = {
    "ATP": sorted(
        path for path in DATA_DIR.glob("[0-9][0-9][0-9][0-9].csv")
        if path.stem != str(CURRENT_YEAR)
    ),
    "WTA": sorted(
        path for path in DATA_DIR.glob("[0-9][0-9][0-9][0-9]_wta.csv")
        if path.stem != f"{CURRENT_YEAR}_wta"
    ),
}
ONGOING_FILES = {
    "ATP": DATA_DIR / "ongoing_tourneys.csv",
    "WTA": DATA_DIR / "wta_ongoing_tourneys.csv",
}
TML_DATA_URLS = {
    "ATP": "https://stats.tennismylife.org/data/{year}.csv",
    "WTA": "https://stats.tennismylife.org/data/{year}_wta.csv",
}
TML_ONGOING_URLS = {
    "ATP": "https://stats.tennismylife.org/data/ongoing_tourneys.csv",
    "WTA": "https://stats.tennismylife.org/data/wta_ongoing_tourneys.csv",
}
POINT_COLUMNS = [
    "w_svpt",
    "w_1stWon",
    "w_2ndWon",
    "l_svpt",
    "l_1stWon",
    "l_2ndWon",
]

PLAYER_NAME_ALIASES = {
    "otic van de zandschulp": "Botic van de Zandschulp",
    "botic van de zandschulp": "Botic van de Zandschulp",
}


def canonicalize_player_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.replace(".", " ")
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text


def standardize_player_name(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    normalized_key = canonicalize_player_name(text)
    if normalized_key in PLAYER_NAME_ALIASES:
        return PLAYER_NAME_ALIASES[normalized_key]
    tokens = [token for token in re.split(r"\s+", text.strip()) if token]
    if not tokens:
        return ""
    title_tokens = [token.title() for token in tokens]
    for particle in ["Van", "De", "Von", "Der", "La", "Le", "Del", "Da", "Di", "El", "Al", "Bin"]:
        title_tokens = [
            token if token.lower() not in {particle.lower()} else particle.lower()
            for token in title_tokens
        ]
    display = " ".join(title_tokens)
    display = re.sub(r"\s+", " ", display).strip()
    return display


def canonicalize_name_columns(frame):
    if frame is None or not isinstance(frame, pd.DataFrame):
        return frame
    for column in ("winner_name", "loser_name"):
        if column in frame.columns:
            frame[f"{column}_key"] = frame[column].map(canonicalize_player_name)
    return frame


def _normalize_point_columns(frame):
    available_columns = [column for column in POINT_COLUMNS if column in frame]
    frame[available_columns] = frame[available_columns].apply(
        pd.to_numeric, errors="coerce"
    )
    return frame


def _load_live_or_local(url, local_file):
    try:
        return pd.read_csv(url) if url else pd.read_csv(local_file)
    except (OSError, ValueError):
        return pd.read_csv(local_file) if local_file.exists() else None

@lru_cache(maxsize=2)
def load_dataset(tour="ATP"):
    """Load local historical data and live current-year data."""
    try:
        tour = tour.upper()
        data_files = DATA_FILES[tour]
    except KeyError as error:
        raise ValueError("tour must be either 'ATP' or 'WTA'") from error

    ongoing_file = ONGOING_FILES[tour]
    current_file = DATA_DIR / (
        f"{CURRENT_YEAR}.csv" if tour == "ATP" else f"{CURRENT_YEAR}_wta.csv"
    )
    frames = [pd.read_csv(data_file) for data_file in data_files]
    live_jobs = [
        (TML_ONGOING_URLS[tour], ongoing_file),
        (TML_DATA_URLS[tour].format(year=CURRENT_YEAR), current_file),
    ]
    with ThreadPoolExecutor(max_workers=2) as executor:
        frames.extend(
            executor.map(lambda job: _load_live_or_local(*job), live_jobs)
        )
    frames = [
        canonicalize_name_columns(_normalize_point_columns(frame))
        for frame in frames
        if frame is not None
    ]
    return pd.concat(frames, ignore_index=True).drop_duplicates(
        subset=["tourney_id", "match_num"], keep="last"
    ).reset_index(drop=True)


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


def filter_dataset_by_mode(df, tour="ATP", mode="Historical"):
    if mode == "Historical":
        return df
    recent_years = sorted(
        int(path.stem.split("_")[0]) for path in DATA_FILES[tour.upper()]
    )[-2:]
    if not recent_years:
        return df.iloc[0:0]
    dates = pd.to_datetime(df["tourney_date"].astype(str), format="%Y%m%d", errors="coerce")
    return df[dates.dt.year >= recent_years[0]]


def player_data_components(
    df, player_name, surface="Hard", tour="ATP", as_of=None
):
    """Return validated surface-specific data components for a player."""
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
    player_key = canonicalize_player_name(player_name)
    winner_df = surface_df[surface_df["winner_name_key"].map(canonicalize_player_name) == player_key]
    loser_df = surface_df[surface_df["loser_name_key"].map(canonicalize_player_name) == player_key]

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
            "serve_points": 0.0,
            "return_points": 0.0,
            "found": False,
        }

    return {
        "serve_baseline": float(default_serve_win),
        "return_baseline": float(default_return_win),
        "winner_serve": winner_serve_df,
        "loser_serve": loser_serve_df,
        "winner_return": winner_return_df,
        "loser_return": loser_return_df,
        "found": True,
    }
