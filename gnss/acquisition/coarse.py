

import numpy

class CoarseAcquirer:
    
    def __init__(self, source, block_length, num_blocks, dopp_bins=None, dopp_min=-5000, dopp_max=5000):
        self.block_length = block_length
        self.num_blocks = num_blocks   
        if not dopp_bins:
            self.dopp_bins = numpy.arange(dopp_min, dopp_max, 1. / block_length)
        else:
            self.dopp_bins = dopp_bins
        self.source = source
        self.num_block_samples = self.block_length * source.f_samp
        self.num_samples = self.num_blocks * self.num_block_samples
        self.correlation = numpy.zeros((len(self.dopp_bins), self.num_block_samples), dtype=numpy.complex)
        self.t = numpy.arange(self.num_block_samples) / source.f_samp
        self.time = None  # TODO fix: undefined until actually calls acquire??
        
    def acquire(self, signal, time=None):
        # correlate
        samples, self.time = self.source.get(self.num_samples, time)
        fft_blocks = numpy.fft.fft(samples[:self.num_samples].reshape((self.num_blocks, self.num_block_samples)), axis=1)
        indices = (numpy.floor(self.t * signal.code.rate) % len(signal.code.sequence)).astype(int)
        code_samples = 1. - 2. * signal.code.sequence[indices]
        for i, f_dopp in enumerate(self.dopp_bins):
            reference = code_samples * numpy.exp(2j * numpy.pi * (self.source.f_center + f_dopp) * self.t)
            conjugate_fft = numpy.conj(numpy.fft.fft(reference))
            self.correlation[i, :] = numpy.sum(numpy.fft.ifft(conjugate_fft * fft_blocks), axis=0) / self.num_blocks
        # perform search
        nsc = int(len(signal.code.sequence) * self.source.f_samp / signal.code.rate)  # number of samples in one code period
        abs_corr = numpy.absolute(self.correlation[:, :nsc])
        f_dopp_i, n0 = numpy.unravel_index(abs_corr.argmax(), abs_corr.shape)
        max_val = abs_corr[f_dopp_i, n0]
        self.snr = 10 * numpy.log(max_val / ((numpy.sum(abs_corr) - max_val) / (abs_corr.size - 1)))
        self.f_dopp = self.dopp_bins[f_dopp_i]
        # chip calculation from sample phase n0: chip = 
        self.chip = (1. - n0 / nsc) * len(signal.code.sequence)
    
    