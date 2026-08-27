import numpy as np

from dataset import load_dataset, player_stats

S_AVG = 0.64
R_AVG = 0.36
DEFAULT_SURFACE = "Hard"


def game_transition_matrix(p):
    q = 1 - p

    Q = np.zeros((15, 15))
    R = np.zeros((15, 2))

    Q[0, 1] = p
    Q[0, 2] = q

    Q[1, 3] = p
    Q[1, 4] = q

    Q[2, 4] = p
    Q[2, 5] = q

    Q[3, 6] = p
    Q[3, 7] = q

    Q[4, 7] = p
    Q[4, 8] = q

    Q[5, 8] = p
    Q[5, 9] = q

    R[6, 0] = p
    Q[6, 10] = q

    Q[7, 10] = p
    Q[7, 12] = q

    Q[8, 12] = p
    Q[8, 11] = q

    Q[9, 11] = p
    R[9, 1] = q

    R[10, 0] = p
    Q[10, 13] = q

    Q[11, 14] = p
    R[11, 1] = q

    Q[12, 13] = p
    Q[12, 14] = q

    R[13, 0] = p
    Q[13, 12] = q

    Q[14, 12] = p
    R[14, 1] = q

    I = np.eye(15)
    N = np.linalg.inv(I - Q)
    A = np.dot(N, R)

    return float(A[0, 0])


def set_transition_matrix(H_1, H_2):
    B_1 = 1 - H_1
    B_2 = 1 - H_2

    Q = np.zeros((39, 39))
    R = np.zeros((39, 2))

    Q[0, 1] = H_1
    Q[0, 2] = B_1

    Q[1, 3] = B_2
    Q[1, 4] = H_2

    Q[2, 4] = B_2
    Q[2, 5] = H_2

    Q[3, 6] = H_1
    Q[3, 7] = B_1

    Q[4, 7] = H_1
    Q[4, 8] = B_1

    Q[5, 8] = H_1
    Q[5, 9] = B_1

    Q[6, 10] = B_2
    Q[6, 11] = H_2

    Q[7, 11] = B_2
    Q[7, 12] = H_2

    Q[8, 12] = B_2
    Q[8, 13] = H_2

    Q[9, 13] = B_2
    Q[9, 14] = H_2

    Q[10, 15] = H_1
    Q[10, 16] = B_1

    Q[11, 16] = H_1
    Q[11, 17] = B_1

    Q[12, 17] = H_1
    Q[12, 18] = B_1

    Q[13, 18] = H_1
    Q[13, 19] = B_1

    Q[14, 19] = H_1
    Q[14, 20] = B_1

    R[15, 0] = B_2
    Q[15, 21] = H_2

    Q[16, 21] = B_2
    Q[16, 22] = H_2

    Q[17, 22] = B_2
    Q[17, 23] = H_2

    Q[18, 23] = B_2
    Q[18, 24] = H_2

    Q[19, 24] = B_2
    Q[19, 25] = H_2

    Q[20, 25] = B_2
    R[20, 1] = H_2

    R[21, 0] = H_1
    Q[21, 26] = B_1

    Q[22, 26] = H_1
    Q[22, 27] = B_1

    Q[23, 27] = H_1
    Q[23, 28] = B_1

    Q[24, 28] = H_1
    Q[24, 29] = B_1

    Q[25, 29] = H_1
    R[25, 1] = B_1

    R[26, 0] = B_2
    Q[26, 30] = H_2

    Q[27, 30] = B_2
    Q[27, 31] = H_2

    Q[28, 31] = B_2
    Q[28, 32] = H_2

    Q[29, 32] = B_2
    R[29, 1] = H_2

    R[30, 0] = H_1
    Q[30, 33] = B_1

    Q[31, 33] = H_1
    Q[31, 34] = B_1

    Q[32, 34] = H_1
    R[32, 1] = B_1

    R[33, 0] = B_2
    Q[33, 35] = H_2

    Q[34, 35] = B_2
    R[34, 1] = H_2

    Q[35, 36] = H_1
    Q[35, 37] = B_1

    R[36, 0] = B_2
    Q[36, 38] = H_2

    Q[37, 38] = B_2
    R[37, 1] = H_2

    R[38, 0] = 0.5
    R[38, 1] = 0.5

    I = np.eye(39)
    N = np.linalg.inv(I - Q)
    A = np.dot(N, R)

    return float(A[0, 0])


def _serve_point_model(serve_pct, opponent_return_pct):
    W_1 = np.sqrt(S_AVG * (1.0 - R_AVG))
    W_2 = np.sqrt((1.0 - S_AVG) * R_AVG)
    numerator = serve_pct * (1.0 - opponent_return_pct) / W_1
    denominator = numerator + ((1.0 - serve_pct) * opponent_return_pct) / W_2
    return float(numerator / denominator)


def compute_player_probabilities(
    player1_name, player2_name, surface=DEFAULT_SURFACE, tour="ATP", as_of=None
):
    df = load_dataset(tour)

    player1_stats = player_stats(df, player1_name, surface, tour, as_of)
    player2_stats = player_stats(df, player2_name, surface, tour, as_of)

    p1_serve = player1_stats["serve_pct"]
    p1_return = player1_stats["return_pct"]
    p2_serve = player2_stats["serve_pct"]
    p2_return = player2_stats["return_pct"]

    p1_point = _serve_point_model(p1_serve, p2_return)
    p2_point = _serve_point_model(p2_serve, p1_return)

    p1_game = game_transition_matrix(p1_point)
    p2_game = game_transition_matrix(p2_point)

    p1_set_if_serves_first = set_transition_matrix(p1_game, p2_game)
    p2_set_if_serves_first = set_transition_matrix(p2_game, p1_game)

    return {
        "player1": {
            "name": player1_name,
            "serve_pct": float(p1_serve),
            "return_pct": float(p1_return),
            "point_win_pct": float(p1_point),
            "game_win_pct": float(p1_game),
            "set_win_pct_if_serves_first": float(p1_set_if_serves_first),
            "found": player1_stats.get("found", False),
        },
        "player2": {
            "name": player2_name,
            "serve_pct": float(p2_serve),
            "return_pct": float(p2_return),
            "point_win_pct": float(p2_point),
            "game_win_pct": float(p2_game),
            "set_win_pct_if_serves_first": float(p2_set_if_serves_first),
            "found": player2_stats.get("found", False),
        },
        "surface": surface,
    }


if __name__ == "__main__":
    stats = compute_player_probabilities("Carlos Alcaraz", "Jannik Sinner")
    print(stats)
