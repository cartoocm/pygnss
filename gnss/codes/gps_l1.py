

def gold_code(feedback_taps, output_taps):
    """Generates Gold code (length 1023 binary sequence) for the given feedback and output taps.
    
    Parameters
    ----------
    feedback_taps : array or ndarray of shape (M,)
        the taps to use for feedback to the shift register's first value
    output_taps : array or ndarray of shape (N,)
        the taps to use for choosing the code output

    Returns
    -------
    output : ndarray of shape(1023,)
        the Gold code sequence

    Notes
    -----
    """
    shift_register = np.ones((10,), dtype=np.uint8)
    code = np.zeros((1023,), dtype=np.uint8)
    for i in range(1023):
        code[i] = np.sum(shift_register[output_taps]) % 2 
        first = np.sum(shift_register[feedback_taps]) % 2 
        shift_register[1:] = shift_register[:-1]
        shift_register[0] = first
    return code
def gps_l1_ca(sv_id):
    """Generates GPS L1 CA PRN code for given SV id.
    
    Parameters
    ----------
    sv_id : int
        the id of the satellite for which the 

    Returns
    -------
    output : ndarray of shape(1023,)
        the complete code sequence

    Notes
    -----
    """
    phase_select = {1: (2, 6), 
                    2: (3, 7), 
                    3: (4, 8), 
                    4: (5, 9), 
                    5: (1, 9), 
                    6: (2, 10),
                    7: (1, 8), 
                    8: (2, 9), 
                    9: (3, 10),
                    10: (2, 3), 
                    11: (3, 4), 
                    12: (5, 6), 
                    13: (6, 7), 
                    14: (7, 8), 
                    15: (8, 9), 
                    16: (9, 10),
                    17: (1, 4), 
                    18: (2, 5), 
                    19: (3, 6), 
                    20: (4, 7), 
                    21: (5, 8), 
                    22: (6, 9), 
                    23: (1, 3), 
                    24: (4, 6), 
                    25: (5, 7), 
                    26: (6, 8), 
                    27: (7, 9), 
                    28: (8, 10),
                    29: (1, 6), 
                    30: (2, 7), 
                    31: (3, 8), 
                    32: (4, 9), 
                    65: (5, 10),
                    66: (4, 10),
                    67: (1, 7), 
                    68: (2, 8), 
                    69: (4, 10)}
    ps = phase_select[sv_id]
    g1 = gold_code([2, 9], [9])
    g2 = gold_code([1, 2, 5, 7, 8, 9], [ps[0] - 1, ps[1] - 1])
    return (g1 + g2) % 2