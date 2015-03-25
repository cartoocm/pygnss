

import numpy
import matplotlib.pyplot as pyplot

class TrackingOutputBuffer:
    
    def __init__(self, **outputs):
        self.outputs = outputs
        self.buffers = {}
        self.indices = {}
        for key in outputs:
            self.buffers[key] = numpy.zeros((outputs[key]['size'],), dtype=outputs[key]['dtype'])
            self.indices[key] = 0
    
    def push(self, **outputs):
        for key in outputs:
            i = self.indices[key] = self.indices[key] + 1
            self.buffers[key][i % self.outputs[key]['size']] = outputs[key]
    
    def clear(self):
        for key in self.outputs:
            self.buffers[key][:] = 0.
            self.indices[key] = 0
            
    def plot(self):
        keys = self.outputs.keys()
        n = len(keys)
        rows = cols = int(numpy.ceil(numpy.sqrt(n)))
        fig = pyplot.figure()
        for i, key in enumerate(keys, 1):
            ax = fig.add_subplot(rows, cols, i)
            ax.plot(self.buffers[key])
            ax.set_title(key)
        return fig
    
    