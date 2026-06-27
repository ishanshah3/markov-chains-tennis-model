import numpy as np

p = 0.64
q = (1 - p)

Q = np.zeros((15,15))
R = np.zeros((15,2))

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

B = np.dot(N, R)

print(B)