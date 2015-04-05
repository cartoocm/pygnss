
import numpy
from numpy import ones, uint8, uint32
from bokeh.plotting import figure

def plot_coarse_acquisition_results(acq):
    c1, c2 = acq.plot_code_window
    r, c = acq.plot_corr.shape
    img = ones((r, c), dtype=uint32)
    view = img.view(dtype=uint8).reshape((r, c, 4))
    view[:, :, 0] = (acq.plot_corr / numpy.max(acq.plot_corr) * 255).astype(uint8)
    view[:, :, 1] = (acq.plot_corr / numpy.max(acq.plot_corr) * 128).astype(uint8)
    view[:, :, 3] = (acq.plot_corr / numpy.max(acq.plot_corr) * 255).astype(uint8)
    dopp_min, dopp_max = acq.dopp_bins[0], acq.dopp_bins[-1]
    p = figure(title='correlation', x_range=[c1, c2], y_range=[dopp_min, dopp_max], 
               x_axis_label='code phase (samples)', y_axis_label='doppler (Hz)')
    p.image_rgba(image=[img], x=[c1], y=[dopp_min], dw=[c2 - c1], dh=[dopp_max - dopp_min])
    return p

def plot_fine_acquisition_results(acquirer):
    p = figure(title='correlation', x_range=[c1, c2], y_range=[dopp_min, dopp_max], 
               x_axis_label='code phase (samples)', y_axis_label='doppler (Hz)')
    p.image_rgba(image=[img], x=[c1], y=[dopp_min], dw=[c2 - c1], dh=[dopp_max - dopp_min])
    return p