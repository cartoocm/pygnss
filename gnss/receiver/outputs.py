

import numpy
import matplotlib.pyplot as pyplot
from bokeh.plotting import GridPlot, VBox, HBox, figure

class TrackingOutputBuffer:
    
    def __init__(self, **outputs):
        self.outputs = outputs
        self.buffers = {}
        self.indices = {}
        for key in outputs:
            self.buffers[key] = numpy.zeros((outputs[key]['size'],), dtype=outputs[key]['dtype'])
            self.buffers[key][:] = numpy.nan
            self.indices[key] = 0
    
    def push(self, **outputs):
        for key in outputs:
            i = self.indices[key]
            self.buffers[key][i % self.outputs[key]['size']] = outputs[key]
            self.indices[key] = self.indices[key] + 1
    
    def clear(self):
        for key in self.outputs:
            self.buffers[key][:] = 0.
            self.indices[key] = 0
            
    def plot(self, library='matplotlib'):
        keys = self.outputs.keys()
        n = len(keys)
        fig = None
        rows = cols = int(numpy.ceil(numpy.sqrt(n)))
        if library is 'matplotlib':
            fig = fig if fig else pyplot.figure()
            for i, key in enumerate(keys, 1):
                ax = fig.add_subplot(rows, cols, i)
                ax.plot(self.buffers[key])
                ax.set_title(key)
            return fig
        elif library is 'bokeh':
            plots = []
            for key in self.outputs.keys():
                plot = figure(title=key, plot_width=250, plot_height=250, tools="pan,wheel_zoom,box_zoom,reset,save")
                plot.line(numpy.arange(self.outputs[key]['size']), self.buffers[key], size=12, alpha=0.7)
                plots.append(plot)
            grid = GridPlot(children=[plots], title="tracking outputs")
            return grid
        return None
    
    