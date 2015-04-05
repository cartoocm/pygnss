
from numpy import sqrt, ceil, arange
import matplotlib.pyplot as pyplot
from bokeh.plotting import GridPlot, VBox, HBox, figure

def plot_outputs(store, library='bokeh'):
    keys = store.outputs.keys()
    n = len(keys)
    fig = None
    rows = cols = int(ceil(sqrt(n)))
    if library is 'matplotlib':
        fig = fig if fig else pyplot.figure()
        for i, key in enumerate(keys, 1):
            ax = fig.add_subplot(rows, cols, i)
            ax.plot(store.buffers[key])
            ax.set_title(key)
        return fig
    elif library is 'bokeh':
        plots = []
        for key in store.outputs.keys():
            plot = figure(title=key, plot_width=250, plot_height=250, tools="pan,wheel_zoom,box_zoom,reset,save")
            plot.line(arange(store.outputs[key]['size']), store.buffers[key], size=12, alpha=0.7)
            plots.append(plot)
        grid = GridPlot(children=[plots], title="tracking outputs")
        return grid
    return None