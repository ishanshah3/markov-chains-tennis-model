import numpy as np

from dataset import serve1, serve2, return1, return2

#LINES 4-9 ARE VARIABLES BASED ON REAL PLAYERS AND THE REAL TOUR AVERAGE PER SURFACE!!!
S_avg = 0.64
R_avg = 0.36
S_1 = serve1
S_2 = serve2
R_1 = return1
R_2 = return2
W_1 = np.sqrt(S_avg * (1 - R_avg))
W_2 = np.sqrt((1 - S_avg) * R_avg)
P_1 = (S_1 * (1 - R_2) / W_1) / ((S_1 * (1 - R_2) / W_1) + (((1 - S_1) * R_2) / W_2))
P_2 = (S_2 * (1 - R_1) / W_1) / ((S_2 * (1 - R_1) / W_1) + (((1 - S_2) * R_1) / W_2))

def game_transition_matrix(p):
    q = (1 - p)

    Q = np.zeros((15, 15))
    R = np.zeros((15, 2))

    # State 0: 0-0
    Q[0, 1] = p
    Q[0, 2] = q

    # State 1: 15-0
    Q[1, 3] = p
    Q[1, 4] = q

    # State 2: 0-15
    Q[2, 4] = p
    Q[2, 5] = q

    # State 3: 30-0
    Q[3, 6] = p
    Q[3, 7] = q

    # State 4: 15-15
    Q[4, 7] = p
    Q[4, 8] = q

    # State 5: 0-30
    Q[5, 8] = p
    Q[5, 9] = q

    # State 6: 40-0
    R[6, 0] = p
    Q[6, 10] = q

    # State 7: 30-15
    Q[7, 10] = p
    Q[7, 12] = q

    # State 8: 15-30
    Q[8, 12] = p
    Q[8, 11] = q

    # State 9: 0-40
    Q[9, 11] = p
    R[9, 1] = q

    # State 10: 40-15
    R[10, 0] = p
    Q[10, 13] = q

    # State 11: 15-40
    Q[11, 14] = p
    R[11, 1] = q

    # State 12: 30-30/40-40(deuce)
    Q[12, 13] = p
    Q[12, 14] = q

    # State 13: 40-30/Ad in
    R[13, 0] = p
    Q[13, 12] = q

    # State 14: 30-40/Ad out
    Q[14, 12] = p
    R[14, 1] = q

    I = np.eye(15)

    N = np.linalg.inv(I - Q)

    A = np.dot(N, R)

    return A[0,0]

H_1 = game_transition_matrix(P_1)
H_2 = game_transition_matrix(P_2)

print(H_1, H_2)

def set_transition_matrix(H_1, H_2, P_1, P_2):
    B_1 = 1 - H_1
    B_2 = 1 - H_2

    Q = np.zeros((39, 39))
    R = np.zeros((39, 2))

    # State 0: 0-0
    Q[0, 1] = H_1
    Q[0, 2] = B_1

    # State 1: 1-0
    Q[1, 3] = B_2
    Q[1, 4] = H_2

    # State 2: 0-1
    Q[2, 4] = B_2
    Q[2, 5] = H_2

    # State 3: 2-0
    Q[3, 6] = H_1
    Q[3, 7] = B_1

    # State 4: 1-1
    Q[4, 7] = H_1
    Q[4, 8] = B_1

    # State 5: 0-2
    Q[5, 8] = H_1
    Q[5, 9] = B_1

    # State 6: 3-0
    Q[6, 10] = B_2
    Q[6, 11] = H_2

    # State 7: 2-1
    Q[7, 11] = B_2
    Q[7, 12] = H_2

    # State 8: 1-2
    Q[8, 12] = B_2
    Q[8, 13] = H_2

    # State 9: 0-3
    Q[9, 13] = B_2
    Q[9, 14] = H_2

    # State 10: 4-0
    Q[10, 15] = H_1
    Q[10, 16] = B_1

    # State 11: 3-1
    Q[11, 16] = H_1
    Q[11, 17] = B_1

    # State 12: 2-2
    Q[12, 17] = H_1
    Q[12, 18] = B_1

    # State 13: 1-3
    Q[13, 18] = H_1
    Q[13, 19] = B_1

    # State 14: 0-4
    Q[14, 19] = H_1
    Q[14, 20] = B_1

    # State 15: 5-0
    R[15, 0] = B_2
    Q[15, 21] = H_2

    # State 16: 4-1
    Q[16, 21] = B_2
    Q[16, 22] = H_2

    # State 17: 3-2
    Q[17, 22] = B_2
    Q[17, 23] = H_2

    # State 18: 2-3
    Q[18, 23] = B_2
    Q[18, 24] = H_2

    # State 19: 1-4
    Q[19, 24] = B_2
    Q[19, 25] = H_2

    # State 20: 0-5
    Q[20, 25] = B_2
    R[20, 1] = H_2

    # State 21: 5-1
    R[21, 0] = H_1
    Q[21, 26] = B_1

    # State 22: 4-2
    Q[22, 26] = H_1
    Q[22, 27] = B_1

    # State 23: 3-3
    Q[23, 27] = H_1
    Q[23, 28] = B_1

    # State 24: 2-4
    Q[24, 28] = H_1
    Q[24, 29] = B_1

    # State 25: 1-5
    Q[25, 29] = H_1
    R[25, 1] = B_1

    # State 26: 5-2
    R[26, 0] = B_2
    Q[26, 30] = H_2

    # State 27: 4-3
    Q[27, 30] = B_2
    Q[27, 31] = H_2

    # State 28: 3-4
    Q[28, 31] = B_2
    Q[28, 32] = H_2

    # State 29: 2-5
    Q[29, 32] = B_2
    R[29, 1] = H_2

    # State 30: 5-3
    R[30, 0] = H_1
    Q[30, 33] = B_1

    # State 31: 4-4
    Q[31, 33] = H_1
    Q[31, 34] = B_1

    # State 32: 3-5
    Q[32, 34] = H_1
    R[32, 1] = B_1

    # State 33: 5-4
    R[33, 0] = B_2
    Q[33, 35] = H_2

    # State 34: 4-5
    Q[34, 35] = B_2
    R[34, 1] = H_2

    # State 35: 5-5
    Q[35, 36] = H_1
    Q[35, 37] = B_1

    # State 36: 6-5
    R[36, 0] = B_2
    Q[36, 38] = H_2

    # State 37: 5-6
    Q[37, 38] = B_2
    R[37, 1] = H_2

    # State 38: 6-6
    R[38, 0] = 0.5
    R[38, 1] = 0.5

    I = np.eye(39)
    N = np.linalg.inv(I - Q)
    A = np.dot(N, R)

    if A[0, 0] > A[0, 1]:
        return("Player 1 wins the match with probability " + str(A[0, 0]) + ".")
    elif A[0, 1] > A[0, 0]:
        return("Player 2 wins the match with probability " + str(A[0, 1]) + ".")
    else:
        return("The match is tied.")

Winner = set_transition_matrix(H_1, H_2, P_1, P_2)
print(Winner)