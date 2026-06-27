import math


def calculate_probabilities(S, R, S1, S2, R1, R2):
    """Calculate the two probability values from percentage inputs.

    All inputs are expected as percentages (0-100).
    Returns a tuple of probabilities in percent.
    """
    S = S / 100.0
    R = R / 100.0
    S1 = S1 / 100.0
    S2 = S2 / 100.0
    R1 = R1 / 100.0
    R2 = R2 / 100.0

    W1 = math.sqrt(S * (1 - R))
    W2 = math.sqrt(R * (1 - S))

    P1 = ((S1 * (1 - R2)) / W1) / (
        ((S1 * (1 - R2)) / W1) + ((1 - S1) * R2) / W2
    )
    P2 = ((S2 * (1 - R1)) / W1) / (
        ((S2 * (1 - R1)) / W1) + ((1 - S2) * R1) / W2
    )

    return P1 * 100.0, P2 * 100.0
