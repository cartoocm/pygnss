

from math import cos, pi
from collections import deque


class IIRFilter:
    """
    Implements a general IIR filter given a set of input and output coefficients.
    """
    def __init__(self, input_coeffs, output_coeffs):
        self.input_coeffs = input_coeffs
        self.output_coeffs = output_coeffs
        self.inputs = deque(maxlen=len(self.input_coeffs))
        self.outputs = deque(maxlen=len(self.output_coeffs))

    def f(self, current_input):
        output = 0
        self.inputs.appendleft(current_input)
        output += sum([c * v for c, v in zip(self.input_coeffs, self.inputs)])
        output += sum([c * v for c, v in zip(self.output_coeffs, self.outputs)])
        self.outputs.appendleft(output)
        return output


def FirstOrderLowpass(bandwidth, fs):
    """
    Creates and returns an IIRFilter with coefficients of a first order 
    lowpass filter.

    inputs
    ------

    bandwidth:
        filter bandwidth
    fs:
        sample frequency
    """
    input_coeffs = []
    output_coeffs = []
    input_coeffs.append( 4. * bandwidth / fs )
    output_coeffs.append( 1. - 4. * bandwidth / fs )
    return IIRFilter(input_coeffs, output_coeffs)

 
def SecondOrderLowpass(omega_n, zeta, fs):
    """
    Creates and returns an IIRFilter with coefficients of a seconds order 
    lowpass filter.

    inputs
    ------

    omega_n:
        filter natural frequency
    zeta:
        filter damping ratio
    fs:
        sample frequency

    TODO: check if a2 is actually really just zeta
    """
    alpha = zeta * omega_n / fs
    beta = (omega_n**2.) / (fs**2.)

    input_coeffs = [alpha + beta,
                    -alpha]

    output_coeffs = [2. - alpha - beta,
                     alpha - 1.]

    return IIRFilter(input_coeffs, output_coeffs)
    

def SecondOrderLowpassV2(omega_n, zeta, fs):
    """
    Creates and returns an IIRFilter with coefficients of a seconds order 
    lowpass filter.

    inputs
    ------

    omega_n:
        filter natural frequency
    zeta:
        filter damping ratio
    fs:
        sample frequency

    TODO: check if a2 is actually really just zeta
    """
    alpha = zeta * omega_n / fs
    beta = (omega_n**2.) / (fs**2.)
    gamma = 2. * alpha + beta + 4.

    input_coeffs = [ (2. * alpha + beta) / gamma,
                      2. * beta / gamma,
                    (-2. * alpha + beta) / gamma ]

    output_coeffs = [(8. - 2. * beta) / gamma,
                     (2. * alpha - beta - 4.) / gamma ]

    return IIRFilter(input_coeffs, output_coeffs)
 

if __name__ == "__main__":
    filter = IIRFilter([0.14, 0.28, 0.57], [.02])
    x = [abs(cos(i / 20. * pi)) for i in range(100)]
    for val in x:
        #print(val)
        print(val, filter.f(val))