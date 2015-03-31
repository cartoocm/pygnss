

import numpy as np
from collections import namedtuple
from gnss.codes.code import Code


class L1CodePhaseAssignment(namedtuple('L1CodePhaseAssignment', 'svid prn ca_phase_select x2_phase_select ca_code_delay p_code_delay first_10_chips_ca first_12_chips_p')):
    """
    (svid, prn, ca_phase_select, x2_phase_select, ca_code_delay, p_code_delay, first_10_chips_ca, first_12_chips_p)
    Tuple struct to store data from Table 3-I of the IS-GPS 200 
    specification, which contains code phase assignment information for GPS L1 signal.
    
    `ca_phase_select` is a 2-tuple in this structure.
    
    `first_12_chips_p`, `first_10_chips_ca` are represented in octal in the table,
    but should just be integer types in this structure.
    
    Note that SVID and PRN numbers differ only for SVIDs 65-69.
    """
    pass

L1_CODE_PHASE_ASSIGNMENTS = {
    1 : L1CodePhaseAssignment(1, 1, (2, 6), 1, 5, 1, 1440, 4444),
    2 : L1CodePhaseAssignment(2, 2, (3, 7), 2, 6, 2, 1620, 4000),
    3 : L1CodePhaseAssignment(3, 3, (4, 8), 3, 7, 3, 1710, 4333),
    4 : L1CodePhaseAssignment(4, 4, (5, 9), 4, 8, 4, 1744, 4377),
    5 : L1CodePhaseAssignment(5, 5, (1, 9), 5, 17, 5, 1133, 4355),
    6 : L1CodePhaseAssignment(6, 6, (2, 10), 6, 18, 6, 1455, 4344),
    7 : L1CodePhaseAssignment(7, 7, (1, 8), 7, 139, 7, 1131, 4340),
    8 : L1CodePhaseAssignment(8, 8, (2, 9), 8, 140, 8, 1454, 4342),
    9 : L1CodePhaseAssignment(9, 9, (3, 10), 9, 141, 9, 1626, 4343),
    10 : L1CodePhaseAssignment(10, 10, (2, 3), 10, 251, 10, 1504, 4343),
    11 : L1CodePhaseAssignment(11, 11, (3, 4), 11, 252, 11, 1642, 4343),
    12 : L1CodePhaseAssignment(12, 12, (5, 6), 12, 254, 12, 1750, 4343),
    13 : L1CodePhaseAssignment(13, 13, (6, 7), 13, 255, 13, 1764, 4343),
    14 : L1CodePhaseAssignment(14, 14, (7, 8), 14, 256, 14, 1772, 4343),
    15 : L1CodePhaseAssignment(15, 15, (8, 9), 15, 257, 15, 1775, 4343),
    16 : L1CodePhaseAssignment(16, 16, (9, 10), 16, 258, 16, 1776, 4343),
    17 : L1CodePhaseAssignment(17, 17, (1, 4), 17, 469, 17, 1156, 4343),
    18 : L1CodePhaseAssignment(18, 18, (2, 5), 18, 470, 18, 1467, 4343),
    19 : L1CodePhaseAssignment(19, 19, (3, 6), 19, 471, 19, 1633, 4343),
    20 : L1CodePhaseAssignment(20, 20, (4, 7), 20, 472, 20, 1715, 4343),
    21 : L1CodePhaseAssignment(21, 21, (5, 8), 21, 473, 21, 1746, 4343),
    22 : L1CodePhaseAssignment(22, 22, (6, 9), 22, 474, 22, 1763, 4343),
    23 : L1CodePhaseAssignment(23, 23, (1, 3), 23, 509, 23, 1063, 4343),
    24 : L1CodePhaseAssignment(24, 24, (4, 6), 24, 512, 24, 1706, 4343),
    25 : L1CodePhaseAssignment(25, 25, (5, 7), 25, 513, 25, 1743, 4343),
    26 : L1CodePhaseAssignment(26, 26, (6, 8), 26, 514, 26, 1761, 4343),
    27 : L1CodePhaseAssignment(27, 27, (7, 9), 27, 515, 27, 1770, 4343),
    28 : L1CodePhaseAssignment(28, 28, (8, 10), 28, 516, 28, 1774, 4343),
    29 : L1CodePhaseAssignment(29, 29, (1, 6), 29, 859, 29, 1127, 4343),
    30 : L1CodePhaseAssignment(30, 30, (2, 7), 30, 860, 30, 1453, 4343),
    31 : L1CodePhaseAssignment(31, 31, (3, 8), 31, 861, 31, 1625, 4343),
    32 : L1CodePhaseAssignment(32, 32, (4, 9), 32, 862, 32, 1712, 4343),
    65 : L1CodePhaseAssignment(65, 33, (5, 10), 33, 863, 33, 1745, 4343),
    66 : L1CodePhaseAssignment(66, 34, (4, 10), 34, 950, 34, 1713, 4343),
    67 : L1CodePhaseAssignment(67, 35, (1, 7), 35, 947, 35, 1134, 4343),
    68 : L1CodePhaseAssignment(68, 36, (2, 8), 36, 948, 36, 1456, 4343),
    69 : L1CodePhaseAssignment(69, 37, (4, 10), 37, 950, 37, 1713, 4343),}

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


CODE_RATE = 1.023e6
NAV_RATE = 50

def gps_l1ca(svid):
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
    ps = L1_CODE_PHASE_ASSIGNMENTS[svid].ca_phase_select
    g1 = gold_code([2, 9], [9])
    g2 = gold_code([1, 2, 5, 7, 8, 9], [ps[0] - 1, ps[1] - 1])
    return Code((g1 + g2) % 2, CODE_RATE)
