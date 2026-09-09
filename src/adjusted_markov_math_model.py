import numpy as np
import pandas as pd

try:
    from dataset import (
        _average_rates,
        canonicalize_player_name,
        filter_dataset_by_mode,
        load_dataset,
        player_data_components,
    )
except ModuleNotFoundError:
    from src.dataset import (
        _average_rates,
        canonicalize_player_name,
        filter_dataset_by_mode,
        load_dataset,
        player_data_components,
    )

HALF_LIFE_DAYS = 180  # days it takes for a player's performance to decay to 50% of its original value)
DEFAULT_SURFACE = "Hard"
BLEND_PRIOR_POINTS = 100 # number of points at tour average to blend with players' actual data to account for uncertainty in small sample sizes


def get_surface_average_rates(surface, tour="ATP", df=None): # finds the tour average serve and return rates for a given surface
    surface = (surface or DEFAULT_SURFACE).title()
    if df is None:
        df = load_dataset(tour)
    surface_df = df[df["surface"] == surface]
    if surface_df.empty:
        surface_df = df
    rates = _average_rates(surface_df) or _average_rates(df)
    serve_avg, return_avg = rates
    return float(serve_avg), float(return_avg)

def game_transition_matrix(p):
    q = 1 - p

    Q = np.zeros((15, 15)) # non-absorbing game score states
    R = np.zeros((15, 2)) # absorbing game score states (0 = player 1 wins, 1 = player 2 wins)

    Q[0, 1] = p # 0-0 to 15-0
    Q[0, 2] = q # 0-0 to 0-15

    Q[1, 3] = p # 15-0 to 30-0
    Q[1, 4] = q # 15-0 to 15-15

    Q[2, 4] = p # 0-15 to 15-15
    Q[2, 5] = q # 0-15 to 0-30

    Q[3, 6] = p # 30-0 to 40-0
    Q[3, 7] = q # 30-0 to 30-15

    Q[4, 7] = p # 15-15 to 30-15
    Q[4, 8] = q # 15-15 to 15-30

    Q[5, 8] = p # 0-30 to 15-30
    Q[5, 9] = q # 0-30 to 0-40

    R[6, 0] = p # 40-0 to player 1 wins
    Q[6, 10] = q # 40-0 to 40-15

    Q[7, 10] = p # 30-15 to 40-15
    Q[7, 12] = q # 30-15 to 30-30

    Q[8, 12] = p # 15-30 to 30-30
    Q[8, 11] = q # 15-30 to 15-40

    Q[9, 11] = p # 0-40 to 15-40
    R[9, 1] = q # 0-40 to player 2 wins

    R[10, 0] = p # 40-15 to player 1 wins
    Q[10, 13] = q # 40-15 to 40-30

    Q[11, 14] = p # 15-40 to 30-40
    R[11, 1] = q # 15-40 to player 2 wins

    Q[12, 13] = p # 30-30/Duece to 40-30/Ad in
    Q[12, 14] = q # 30-30/Duece to 30-40/Ad out

    R[13, 0] = p # 40-30/Ad in to player 1 wins
    Q[13, 12] = q # 40-30/Ad in to Duece

    Q[14, 12] = p # 30-40/Ad out to Duece
    R[14, 1] = q # 30-40/Ad out to player 2 wins

    I = np.eye(15) # identity matrix for the non-absorbing states
    N = np.linalg.inv(I - Q) # fundamental matrix for the non-absorbing states
    A = np.dot(N, R) # matrix of probabilities of reaching each absorbing state from each non-absorbing state

    return float(A[0, 0])


def set_transition_matrix(H_1, H_2):
    B_1 = 1 - H_1
    B_2 = 1 - H_2

    Q = np.zeros((39, 39)) # non-absorbing set score states
    R = np.zeros((39, 2)) # absorbing set score states (0 = player 1 wins, 1 = player 2 wins)

    Q[0, 1] = H_1 # 0-0 to 1-0
    Q[0, 2] = B_1 # 0-0 to 0-1

    Q[1, 3] = B_2 # 1-0 to 2-0
    Q[1, 4] = H_2 # 1-0 to 1-1

    Q[2, 4] = B_2 # 0-1 to 1-1
    Q[2, 5] = H_2 # 0-1 to 0-2

    Q[3, 6] = H_1 # 2-0 to 3-0
    Q[3, 7] = B_1 # 2-0 to 2-1

    Q[4, 7] = H_1 # 1-1 to 2-1
    Q[4, 8] = B_1 # 1-1 to 1-2

    Q[5, 8] = H_1 # 0-2 to 1-2
    Q[5, 9] = B_1 # 0-2 to 0-3

    Q[6, 10] = B_2 # 3-0 to 4-0
    Q[6, 11] = H_2 # 3-0 to 3-1

    Q[7, 11] = B_2 # 2-1 to 3-1
    Q[7, 12] = H_2 # 2-1 to 2-2

    Q[8, 12] = B_2 # 1-2 to 2-2
    Q[8, 13] = H_2 # 1-2 to 1-3

    Q[9, 13] = B_2 # 0-3 to 1-3
    Q[9, 14] = H_2 # 0-3 to 0-4

    Q[10, 15] = H_1 # 4-0 to 5-0
    Q[10, 16] = B_1 # 4-0 to 4-1

    Q[11, 16] = H_1 # 3-1 to 4-1
    Q[11, 17] = B_1 # 3-1 to 3-2

    Q[12, 17] = H_1 # 2-2 to 3-2
    Q[12, 18] = B_1 # 2-2 to 2-3

    Q[13, 18] = H_1 # 1-3 to 2-3
    Q[13, 19] = B_1 # 1-3 to 1-4

    Q[14, 19] = H_1 # 0-4 to 1-4
    Q[14, 20] = B_1 # 0-4 to 0-5

    R[15, 0] = B_2 # 5-0 to player 1 wins
    Q[15, 21] = H_2 # 5-0 to 5-1

    Q[16, 21] = B_2 # 4-1 to 5-1
    Q[16, 22] = H_2 # 4-1 to 4-2

    Q[17, 22] = B_2 # 3-2 to 4-2
    Q[17, 23] = H_2 # 3-2 to 3-3

    Q[18, 23] = B_2 # 2-3 to 3-3
    Q[18, 24] = H_2 # 2-3 to 2-4

    Q[19, 24] = B_2 # 1-4 to 2-4
    Q[19, 25] = H_2 # 1-4 to 1-5

    Q[20, 25] = B_2 # 0-5 to 1-5
    R[20, 1] = H_2 # 0-5 to player 2 wins

    R[21, 0] = H_1 # 5-1 to player 1 wins
    Q[21, 26] = B_1 # 5-1 to 5-2

    Q[22, 26] = H_1 # 4-2 to 5-2
    Q[22, 27] = B_1 # 4-2 to 4-3

    Q[23, 27] = H_1 # 3-3 to 4-3
    Q[23, 28] = B_1 # 3-3 to 3-4

    Q[24, 28] = H_1 # 2-4 to 3-4
    Q[24, 29] = B_1 # 2-4 to 2-5

    Q[25, 29] = H_1 # 1-5 to 2-5
    R[25, 1] = B_1 # 1-5 to player 2 wins

    R[26, 0] = B_2 # 5-2 to player 1 wins
    Q[26, 30] = H_2 # 5-2 to 5-3

    Q[27, 30] = B_2 # 4-3 to 5-3
    Q[27, 31] = H_2 # 4-3 to 4-4

    Q[28, 31] = B_2 # 3-4 to 4-4
    Q[28, 32] = H_2 # 3-4 to 3-5

    Q[29, 32] = B_2 # 2-5 to 3-5
    R[29, 1] = H_2 # 2-5 to player 2 wins

    R[30, 0] = H_1 # 5-3 to player 1 wins
    Q[30, 33] = B_1 # 5-3 to 5-4

    Q[31, 33] = H_1 # 4-4 to 5-4
    Q[31, 34] = B_1 # 4-4 to 4-5

    Q[32, 34] = H_1 # 3-5 to 4-5
    R[32, 1] = B_1 # 3-5 to player 2 wins

    R[33, 0] = B_2 # 5-4 to player 1 wins
    Q[33, 35] = H_2 # 5-4 to 5-5

    Q[34, 35] = B_2 # 4-5 to 5-5
    R[34, 1] = H_2 # 4-5 to player 2 wins

    Q[35, 36] = H_1 # 5-5 to 6-5
    Q[35, 37] = B_1 # 5-5 to 5-6

    R[36, 0] = B_2 # 6-5 to player 1 wins
    Q[36, 38] = H_2 # 6-5 to 6-6

    Q[37, 38] = B_2 # 5-6 to 6-6
    R[37, 1] = H_2 # 5-6 to player 2 wins

    R[38, 0] = 0.5 # 6-6 to player 1 wins (tiebreaker - tentative)
    R[38, 1] = 0.5 # 6-6 to player 2 wins (tiebreaker - tentative)

    I = np.eye(39) # identity matrix for the non-absorbing states
    N = np.linalg.inv(I - Q) # fundamental matrix for the non-absorbing states
    A = np.dot(N, R) # matrix of probabilities of reaching each absorbing state from each non-absorbing state

    return float(A[0, 0])


def _serve_point_model(serve_pct, opponent_return_pct, serve_avg=None, return_avg=None): # calculates the probability of winning a point on serve given a player's serve percentage and the opponent's return percentage, adjusted for surface averages
    W_1 = np.sqrt(serve_avg * (1.0 - return_avg)) # average serve win %
    W_2 = np.sqrt((1.0 - serve_avg) * return_avg) # average return win %
    numerator = serve_pct * (1.0 - opponent_return_pct) / W_1
    denominator = numerator + ((1.0 - serve_pct) * opponent_return_pct) / W_2
    return float(numerator / denominator) # adjusted probability of winning a point on serve given the player's serve percentage and the opponent's return percentage, adjusted for surface averages


def _weighted_player_rates(stats, as_of, use_decay=True):
    if not stats["found"]:
        baseline_serve = stats.get("serve_baseline", stats["serve_pct"])
        baseline_return = stats.get("return_baseline", stats["return_pct"])
        return baseline_serve, baseline_return, True

    def weighted_sum(values, frame):
        weights = 0.5 ** (
            (as_of - frame["tourney_date"]).dt.days / HALF_LIFE_DAYS
        )
        return float(values.mul(weights).sum())

    winner_serve = stats["winner_serve"]
    loser_serve = stats["loser_serve"]
    winner_return = stats["winner_return"]
    loser_return = stats["loser_return"]
    raw_serve_points = winner_serve["w_svpt"].sum() + loser_serve["l_svpt"].sum()
    raw_return_points = winner_return["l_svpt"].sum() + loser_return["w_svpt"].sum()
    raw_serve_won = (
        winner_serve["w_1stWon"].sum()
        + winner_serve["w_2ndWon"].sum()
        + loser_serve["l_1stWon"].sum()
        + loser_serve["l_2ndWon"].sum()
    )
    raw_return_won = (
        winner_return["l_svpt"].sum()
        - winner_return["l_1stWon"].sum()
        - winner_return["l_2ndWon"].sum()
        + loser_return["w_svpt"].sum()
        - loser_return["w_1stWon"].sum()
        - loser_return["w_2ndWon"].sum()
    )
    low_confidence = bool(raw_serve_points < 500 or raw_return_points < 500)
    if raw_serve_points == 0 or raw_return_points == 0:
        baseline_serve = stats["serve_baseline"]
        baseline_return = stats["return_baseline"]
        return baseline_serve, baseline_return, True
    if use_decay:
        decay_serve_points = weighted_sum(winner_serve["w_svpt"], winner_serve)
        decay_serve_points += weighted_sum(loser_serve["l_svpt"], loser_serve)
        decay_serve_won = weighted_sum(winner_serve["w_1stWon"], winner_serve)
        decay_serve_won += weighted_sum(winner_serve["w_2ndWon"], winner_serve)
        decay_serve_won += weighted_sum(loser_serve["l_1stWon"], loser_serve)
        decay_serve_won += weighted_sum(loser_serve["l_2ndWon"], loser_serve)
        decay_return_points = weighted_sum(winner_return["l_svpt"], winner_return)
        decay_return_points += weighted_sum(loser_return["w_svpt"], loser_return)
        decay_return_won = weighted_sum(
            winner_return["l_svpt"]
            - winner_return["l_1stWon"]
            - winner_return["l_2ndWon"],
            winner_return,
        )
        decay_return_won += weighted_sum(
            loser_return["w_svpt"]
            - loser_return["w_1stWon"]
            - loser_return["w_2ndWon"],
            loser_return,
        )
        serve_rate = decay_serve_won / decay_serve_points
        return_rate = decay_return_won / decay_return_points
    else:
        serve_rate = raw_serve_won / raw_serve_points
        return_rate = raw_return_won / raw_return_points
    serve_rate = (
        raw_serve_points * serve_rate
        + BLEND_PRIOR_POINTS * stats["serve_baseline"]
    ) / (raw_serve_points + BLEND_PRIOR_POINTS)
    return_rate = (
        raw_return_points * return_rate
        + BLEND_PRIOR_POINTS * stats["return_baseline"]
    ) / (raw_return_points + BLEND_PRIOR_POINTS)
    return float(serve_rate), float(return_rate), low_confidence


def compute_player_probabilities(
    player1_name,
    player2_name,
    surface=DEFAULT_SURFACE,
    tour="ATP",
    as_of=None,
    mode="Historical",
):
    df = load_dataset(tour)
    current_df = filter_dataset_by_mode(df, tour, "Current")
    analysis_df = df
    current_player_keys = set(current_df["winner_name_key"]) | set(
        current_df["loser_name_key"]
    )

    player1_stats = player_data_components(
        analysis_df, player1_name, surface, tour, as_of
    )
    player2_stats = player_data_components(
        analysis_df, player2_name, surface, tour, as_of
    )

    as_of = pd.Timestamp.today().normalize() if as_of is None else pd.Timestamp(as_of)
    p1_use_decay = mode != "Historical" or canonicalize_player_name(
        player1_name
    ) in current_player_keys
    p2_use_decay = mode != "Historical" or canonicalize_player_name(
        player2_name
    ) in current_player_keys
    p1_serve, p1_return, p1_low_confidence = _weighted_player_rates(
        player1_stats, as_of, use_decay=p1_use_decay
    )
    p2_serve, p2_return, p2_low_confidence = _weighted_player_rates(
        player2_stats, as_of, use_decay=p2_use_decay
    )

    serve_avg, return_avg = get_surface_average_rates(surface, tour, df)
    p1_point = _serve_point_model(p1_serve, p2_return, serve_avg=serve_avg, return_avg=return_avg)
    p2_point = _serve_point_model(p2_serve, p1_return, serve_avg=serve_avg, return_avg=return_avg)

    p1_game = game_transition_matrix(p1_point)
    p2_game = game_transition_matrix(p2_point)

    p1_set_win = set_transition_matrix(p1_game, p2_game)
    p2_set_win = 1.0 - p1_set_win

    return {
        "player1": {
            "name": player1_name,
            "serve_pct": float(p1_serve),
            "return_pct": float(p1_return),
            "point_win_pct": float(p1_point),
            "game_win_pct": float(p1_game),
            "set_win_pct": float(p1_set_win),
            "found": player1_stats.get("found", False),
            "low_confidence": bool(p1_low_confidence),
        },
        "player2": {
            "name": player2_name,
            "serve_pct": float(p2_serve),
            "return_pct": float(p2_return),
            "point_win_pct": float(p2_point),
            "game_win_pct": float(p2_game),
            "set_win_pct": float(p2_set_win),
            "found": player2_stats.get("found", False),
            "low_confidence": bool(p2_low_confidence),
        },
        "surface": surface,
    }


if __name__ == "__main__":
    stats = compute_player_probabilities("Carlos Alcaraz", "Jannik Sinner")
    print(stats)
