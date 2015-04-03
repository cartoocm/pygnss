
from fractions import gcd
from numpy import arange, floor, vstack, asarray, repeat

def lcm(a, b):
    """
    Finds the least common mutliple of two integers `a` and `b`.
    Stolen from: http://rosettacode.org/wiki/Least_common_multiple#Python
    """
    return abs(a * b) / gcd(a, b) if a and b else 0
    
    
class Code:
    
    def __init__(self, sequence, rate):
        self.sequence = asarray(sequence)
        self.rate = rate
    
    def __getitem__(self, key):
        return self.sequence[key]
    
    def __xor__(self, other):
        if len(self.sequence) != len(other.sequence):
            raise ValueError('Code sequence lengths must be the same. Use Code.combine instead')
        if self.rate != other.rate:
            raise ValueError('Code rates must be the same. Use Code.combine instead')
        return Code((self.sequence + other.sequence) % 2, self.rate)
    
    @property
    def length(self):
        return len(self.sequence)
    
    def time_multiplex(code_1, code_2):
        """
        Given two codes `code_1` and `code_2` returns a combined code of the 
        interleaved sequences of `code_1` and `code_2` at twice the rate of 
        `code_1`/`code_2` and of length of the longer sequence.
        """
        assert(code_1.rate == code_2.rate)
        rate = code_1.rate
        new_rate = rate * 2
        length = max(len(code_1.sequence), len(code_2.sequence))
        indices = arange(length)
        sequence_1 = code_1.sequence[indices % len(code_1.sequence)]
        sequence_2 = code_2.sequence[indices % len(code_2.sequence)]
#         t = arange(0., new_length / new_rate, 1. / rate)
#         sequence_1 = code_1.sequence[(floor(t * rate) % len(code_1.sequence)).astype(int)]
#         sequence_2 = code_2.sequence[(floor(t * rate) % len(code_2.sequence)).astype(int)]
        # the following concatenates the arrays along their unit-dimensions (say, puts them into two rows)
        # then reshapes them so they interleave into one long vector.
        new_sequence = vstack((sequence_1, sequence_2)).reshape((-1,), order='F')
        return Code(new_sequence, new_rate)
    
    def combine(code_1, code_2, new_length, new_rate):
        """
        Given two codes `code_1` and `code_2` and the new length and rate for a combined code,
        returns the modulo-2 sum of the two codes of new length at the new rate.
        
        NOTE/TODO: seems to not be working with GPS L5 I+neuman hoffman overlay, use overlay instead
        """
        t = arange(0., new_length / new_rate, 1. / new_rate)
        sequence = (code_1.sequence[(floor(t * code_1.rate) % len(code_1.sequence)).astype(int)] \
                  + code_2.sequence[(floor(t * code_2.rate) % len(code_2.sequence)).astype(int)]) % 2
        return Code(sequence, new_rate)

    def overlay(code, overlay_code):
        """
        Given `code`, assumes each overlay chip in `overlay_code` lasts one period of `code`.
        Creates and returns new code of length `code.length * overlay_code.length` of the
        original code modulo-2 summed with the overlay.
        """
        code_seq = repeat(asarray([code.sequence]), overlay_code.length, axis=0).flatten()
        overlay_seq = repeat(overlay_code.sequence, code.length)
        return Code((code_seq + overlay_seq) % 2, code.rate)