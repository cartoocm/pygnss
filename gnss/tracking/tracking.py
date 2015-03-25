
import numpy


def code_samples(signal, f_dopp, t, chip=0.):
    f_chip = signal.code.rate * (1. + f_dopp / signal.f_carrier)
    return 1. - 2. * signal.code.sequence[(numpy.floor(chip + t * f_chip) % len(signal.code.sequence)).astype(int)]


class Correlator:
    
    def __init__(self, chip_delays=[-.5, 0., .5], doppler_offsets=[]):
        self.chip_delays = chip_delays
        self.doppler_offsets = doppler_offsets
    
    def correlate(self, signal, source, block_size, time, chip, f_dopp, theta):
        samples, time = source.get(block_size, time)
        # TODO handle changes in time
        t = numpy.arange(block_size) / source.f_samp
        carrierless = samples * numpy.exp(-2j * numpy.pi * (source.f_center + f_dopp) * t - 1j * theta)
        codeless = samples * code_samples(signal, f_dopp, t, chip)
        chip_delay_outputs = (numpy.sum(carrierless * code_samples(signal, f_dopp, t, chip + delay)) \
                              for delay in self.chip_delays)
        doppler_offset_outputs = (np.sum(codeless \
                    * numpy.exp(-2j * numpy.pi * (source.f_center + f_dopp + dopp_offset) * t - 1j * theta)) \
                    for dopp_offset in self.doppler_offsets)
        return chip_delay_outputs, doppler_offset_outputs
    
    
def delay_discriminator(early, prompt, late, delay=.5):
    return delay * (numpy.abs(early) - numpy.abs(late)) / (numpy.abs(late) + numpy.abs(early) + 2 * numpy.abs(prompt))

def costas_discriminator(prompt):
    '''
    Return Costas discriminator output for phase.
    '''
    return numpy.real(prompt) * numpy.imag(prompt) / numpy.abs(prompt)**2