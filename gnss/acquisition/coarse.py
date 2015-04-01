

import numpy
from bokeh.plotting import figure

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
        # for plotting later vvv
        self.plot_corr = None
        self.plot_code_window = None
        
    def acquire(self, signal, time=None):
        # correlate
        samples, self.time = self.source.get(self.num_samples, time)
        fft_blocks = numpy.fft.fft(samples[:self.num_samples].reshape((self.num_blocks, self.num_block_samples)), axis=1)
        indices = (numpy.floor(self.t * signal.code.rate) % len(signal.code.sequence)).astype(int)
        code_samples = 1. - 2. * signal.code.sequence[indices]
        f_inter = signal.f_carrier - self.source.f_center
        for i, f_dopp in enumerate(self.dopp_bins):
            reference = code_samples * numpy.exp(2j * numpy.pi * (f_inter + f_dopp) * self.t)
            conjugate_fft = numpy.conj(numpy.fft.fft(reference))
            self.correlation[i, :] = numpy.sum(numpy.fft.ifft(conjugate_fft * fft_blocks), axis=0) / self.num_blocks
        # perform search
        nsc = int(len(signal.code.sequence) * self.source.f_samp / signal.code.rate)  # number of samples in one code period
        abs_corr = numpy.absolute(self.correlation[:, :nsc])
        abs_corr /= numpy.mean(abs_corr)
        f_dopp_i, n0 = numpy.unravel_index(abs_corr.argmax(), abs_corr.shape)
        max_val = abs_corr[f_dopp_i, n0]
        self.snr = 10 * numpy.log((max_val - 1.) / numpy.std(abs_corr))
        self.f_dopp = self.dopp_bins[f_dopp_i]
        # chip calculation from sample phase n0: chip = 
        self.chip = (1. - n0 / nsc) * len(signal.code.sequence)
        
        # for plotting later
        img_width = 300
        c1 = int(max(0, n0 - img_width // 2))
        c2 = min(abs_corr.shape[1], c1 + img_width)
        self.plot_corr = abs_corr[:, c1:c2]
        self.plot_code_window = (c1, c2)
        
    def plot(self):
        c1, c2 = self.plot_code_window
        r, c = self.plot_corr.shape
        img = numpy.ones((r, c), dtype=numpy.uint32)
        view = img.view(dtype=numpy.uint8).reshape((r, c, 4))
        view[:, :, 0] = (self.plot_corr / numpy.max(self.plot_corr) * 255).astype(numpy.uint8)
        view[:, :, 1] = (self.plot_corr / numpy.max(self.plot_corr) * 128).astype(numpy.uint8)
        view[:, :, 3] = (self.plot_corr / numpy.max(self.plot_corr) * 255).astype(numpy.uint8)
        dopp_min, dopp_max = self.dopp_bins[0], self.dopp_bins[-1]
        p = figure(title='correlation', x_range=[c1, c2], y_range=[dopp_min, dopp_max], 
                   x_axis_label='code phase (samples)', y_axis_label='doppler (Hz)')
        p.image_rgba(image=[img], x=[c1], y=[dopp_min], dw=[c2 - c1], dh=[dopp_max - dopp_min])
        return p
    