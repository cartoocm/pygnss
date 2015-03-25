


import numpy


class FineAcquirer:
    
    # when acquire, call next block on source, get and store acquisition start time as acquisition epoch
    
    def __init__(self, source, block_length, separation_length, num_blocks):
        self.source = source
        self.block_length = block_length
        self.separation_length = separation_length
        self.num_blocks = num_blocks
        self.num_block_samples = self.block_length * source.f_samp
        self.num_sep_samples = self.separation_length * source.f_samp
        self.num_samples = self.num_blocks * self.num_sep_samples + self.num_block_samples
        self.phases = numpy.zeros((self.num_blocks,), dtype=numpy.complex)
        self.t = numpy.arange(self.num_samples) / source.f_samp
    
    def acquire(self, signal, time, chip, f_dopp):
        # time is the time of acquisition of parameters chip and f_dopp
        # TODO come up with a better way to pass these parameters
        # doppler adjusted chipping rate
        f_chip = signal.code.rate * (1 + f_dopp / signal.f_carrier)
        # get signal samples and correct for quantization
        samples, self.time = self.source.get(self.num_samples, time)
        # correct for any time quantization
        chip += (self.time - time) * f_chip
        # generate code samples
        indices = (numpy.floor(chip + self.t * f_chip) % len(signal.code.sequence)).astype(int)
        code_samples = 1. - 2. * signal.code.sequence[indices]
        # generate reference and clean signal
        conjugate_reference = code_samples * numpy.exp(-2j * numpy.pi * (self.source.f_center + f_dopp) * self.t)
        clean_signal = conjugate_reference * samples
        # sum and store phases
        for i in range(self.num_blocks):
            self.phases[i] = numpy.sum(clean_signal[i * self.num_sep_samples:i * self.num_sep_samples + self.num_block_samples])
        d_angles = numpy.angle(self.phases[1:] / self.phases[:-1])
        indices = numpy.where((d_angles - d_angles.mean())**2 < d_angles.var())[0]
        slope = numpy.mean(d_angles[indices])
        delta_f_dopp = slope / (self.separation_length * 2 * numpy.pi)
        self.f_dopp = f_dopp + delta_f_dopp
        
        