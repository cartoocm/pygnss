
from fractions import gcd
from numpy import arange, floor

b = arange(1, 3)

class Code:
    
    def __init__(self, sequence, rate):
        self.sequence = sequence
        self.rate = rate
    
    def time_multiplex(code_1, code_2, new_length):
        """
        Given two codes `code_1` and `code_2` and a new length for the combined code,
        returns a combined code of the interleaved sequences of `code_1` and `code_2` at
        twice the rate of `code_1`/`code_2`.
        """
        assert(code_1.rate == code_2.rate)
        rate = code_1.rate
        new_rate = rate * 2
        t = arange(0., new_length / new_rate, 1. / rate)
        sequence_1 = code_1.sequence[floor(t * rate) % len(code_1.sequence)]
        sequence_2 = code_2.sequence[floor(t * rate) % len(code_2.sequence)]
        # the following concatenates the arrays along their unit-dimensions (say, puts them into two rows)
        # then reshapes them so they interleave into one long vector.
        new_sequence = vstack((sequence_1, sequence_2)).reshape((-1,), order='F')
        return Code(new_sequence, new_rate)
    
    def lcm(a, b):
        """
        Finds the least common mutliple of two integers `a` and `b`.
        Stolen from: http://rosettacode.org/wiki/Least_common_multiple#Python
        """
        return abs(a * b) / gcd(a, b) if a and b else 0
    
    def combine(code_1, code_2, new_length, new_rate):
        """
        Given two codes `code_1` and `code_2` and the new length and rate for a combined code,
        returns the modulo-2 sum of the two codes of new length at the new rate.
        """
        t = arange(0., new_length / new_rate, 1. / new_rate)
        sequence = (code_1.sequence[(floor(t * code_1.rate) % len(code_1.sequence)).astype(int)] \
                  + code_2.sequence[(floor(t * code_2.rate) % len(code_2.sequence)).astype(int)]) % 2
        return Code(sequence, new_rate)