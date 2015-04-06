
import numpy
npmax = numpy.max
from numpy import ones, uint8, uint32, arange, angle, unwrap
from bokeh.plotting import figure
from gnss.acquisition import CoarseAcquirer, CoarseAcquirerLowMem, FineAcquirer

def plot_coarse_acquisition_results(acq):
    if type(acq) is CoarseAcquirerLowMem:
        dopp_min, dopp_max = acq.dopp_bins[0], acq.dopp_bins[-1]
        p = figure(title='correlation', x_range=[dopp_min, dopp_max], 
                x_axis_label='doppler (Hz)', y_axis_label='correlation strength')
        p.line(acq.dopp_bins, acq.corr_max)
        return p
    elif type(acq) is CoarseAcquirer:
        c1, c2 = acq.plot_code_window
        r, c = acq.plot_corr.shape
        img = ones((r, c), dtype=uint32)
        view = img.view(dtype=uint8).reshape((r, c, 4))
        view[:, :, 0] = (acq.plot_corr / npmax(acq.plot_corr) * 255).astype(uint8)
        view[:, :, 1] = (acq.plot_corr / npmax(acq.plot_corr) * 128).astype(uint8)
        view[:, :, 3] = (acq.plot_corr / npmax(acq.plot_corr) * 255).astype(uint8)
        dopp_min, dopp_max = acq.dopp_bins[0], acq.dopp_bins[-1]
        p = figure(title='correlation', x_range=[c1, c2], y_range=[dopp_min, dopp_max], 
                x_axis_label='code phase (samples)', y_axis_label='doppler (Hz)')
        p.image_rgba(image=[img], x=[c1], y=[dopp_min], dw=[c2 - c1], dh=[dopp_max - dopp_min])
        return p


def plot_fine_acquisition_results(acq):
    if type(acq) is FineAcquirer:
        p = figure(title='fine phase', x_axis_label='time (s)', y_axis_label='phase (rad)')
        t = arange(len(acq.phases)) * acq.block_length
        p.line(t, unwrap(angle(acq.phases)))
        return p
