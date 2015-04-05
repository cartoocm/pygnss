
from collections import OrderedDict
from numpy import zeros, nan, arange, ceil, sqrt

class TrackingOutputBuffer:
    
    def __init__(self, **outputs):
        self.outputs = outputs
        self.buffers = OrderedDict()
        self.indices = {}
        for key in outputs:
            self.buffers[key] = zeros((outputs[key]['size'],), dtype=outputs[key]['dtype'])
            self.buffers[key][:] = nan
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