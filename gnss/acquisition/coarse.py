
import numpy
from numpy import arange, zeros, complex64, floor, exp, absolute, conj, mean, unravel_index, std, log, argmax, pi, var, std
npsum = numpy.sum
npmax = numpy.max
fft = numpy.fft.fft
ifft = numpy.fft.ifft

class CoarseAcquirer:
    
    def __init__(self, source, block_length, num_blocks, dopp_bins=None, dopp_min=-5000, dopp_max=5000):
        self.block_length = block_length
        self.num_blocks = num_blocks   
        if dopp_bins is None:
            self.dopp_bins = arange(dopp_min, dopp_max, 1. / block_length)
        else:
            self.dopp_bins = dopp_bins
        self.source = source
        self.num_block_samples = self.block_length * source.f_samp
        self.num_samples = self.num_blocks * self.num_block_samples
        self.correlation = zeros((len(self.dopp_bins), self.num_block_samples), dtype=complex64)
        self.t = arange(self.num_block_samples) / source.f_samp
        self.time = None  # TODO fix: undefined until actually calls acquire??
        # for plotting later vvv
        self.plot_corr = None
        self.plot_code_window = None
       
    @property
    def cn0(self):
        return self.snr + 10 * log(1 / self.block_length)
        
    def acquire(self, signal, time=None):
        # correlate
        samples, self.time = self.source.get(self.num_samples, time)
        fft_blocks = fft(samples[:self.num_samples].reshape((self.num_blocks, self.num_block_samples)), axis=1)
        indices = (floor(self.t * signal.code.rate) % len(signal.code.sequence)).astype(int)
        code_samples = 1. - 2. * signal.code.sequence[indices]
        f_inter = signal.f_carrier - self.source.f_center
        for i, f_dopp in enumerate(self.dopp_bins):
            reference = code_samples * exp(2j * pi * (f_inter + f_dopp) * self.t)
            conjugate_fft = conj(fft(reference))
            self.correlation[i, :] = npsum(ifft(conjugate_fft * fft_blocks), axis=0) / self.num_blocks
        # perform search
        nsc = int(signal.code.length * self.source.f_samp / signal.code.rate)  # number of samples in one code period
        abs_corr = absolute(self.correlation[:, :nsc])
        abs_corr /= mean(abs_corr)
        dopp_bin, n0 = unravel_index(abs_corr.argmax(), abs_corr.shape)
        max_val = abs_corr[dopp_bin, n0]
        self.snr = 10 * log((max_val - 1.) / std(abs_corr))
        self.f_dopp = self.dopp_bins[dopp_bin]
        # chip calculation from sample phase n0: chip = 
        self.chip = (1. - n0 / nsc) * len(signal.code.sequence)
        
        # for plotting later
        img_width = 300
        c1 = int(max(0, n0 - img_width // 2))
        c2 = min(abs_corr.shape[1], c1 + img_width)
        self.plot_corr = abs_corr[:, c1:c2]
        self.plot_code_window = (c1, c2)
       
    
# Noise equiv bw is just 1/T and cn0 = snr + bw(in db) so that really long integration times are effectively just the ratio snr
class CoarseAcquirerLowMem(CoarseAcquirer):
    
    def __init__(self, source, block_length, num_blocks, dopp_bins=None, dopp_min=-5000, dopp_max=5000):
        self.block_length = block_length
        self.num_blocks = num_blocks   
        if dopp_bins is None:
            self.dopp_bins = arange(dopp_min, dopp_max, 1. / block_length)
        else:
            self.dopp_bins = dopp_bins
        self.source = source
        self.num_block_samples = self.block_length * source.f_samp
        self.num_samples = self.num_blocks * self.num_block_samples
        self.t = arange(self.num_block_samples) / source.f_samp
        self.time = None
        
    def acquire(self, signal, time=None):
        # correlate
        samples, self.time = self.source.get(self.num_samples, time)
        fft_blocks = fft(samples[:self.num_samples].reshape((self.num_blocks, self.num_block_samples)), axis=1)
        indices = (floor(self.t * signal.code.rate) % len(signal.code.sequence)).astype(int)
        code_samples = 1. - 2. * signal.code.sequence[indices]
        f_inter = signal.f_carrier - self.source.f_center
        corr_max = zeros((len(self.dopp_bins),))  # value
        n0 = zeros((len(self.dopp_bins),))  # n0
        corr_std = corr_var = 0.
        for i, f_dopp in enumerate(self.dopp_bins):
            reference = code_samples * exp(2j * pi * (f_inter + f_dopp) * self.t)
            conjugate_fft = conj(fft(reference))
            correlation = absolute(npsum(ifft(conjugate_fft * fft_blocks), axis=0)) / self.num_blocks
            corr_max[i] = npmax(correlation)  # value
            n0[i] = argmax(correlation)  # n0
            corr_std += std(correlation)
            corr_var += var(correlation)
        # perform search
        nsc = int(signal.code.length * self.source.f_samp / signal.code.rate)  # number of samples in one code period
        corr_std /= len(self.dopp_bins)
        corr_var /= len(self.dopp_bins)
        # corr_std is noise floor, corr_var is noise power
        dopp_bin = argmax(corr_max)
        self.f_dopp = self.dopp_bins[dopp_bin]
        self.n0 = n0[dopp_bin] % nsc
        self.chip = (1. - self.n0 / nsc) * len(signal.code.sequence)
        self.snr = 10 * log((corr_max[dopp_bin] - 1.) / corr_std)        
        
        # for plotting later
        self.corr_max = corr_max