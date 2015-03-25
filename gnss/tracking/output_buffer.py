

class TrackingOutputBuffer:
    
    def __init__(self, **outputs):
        self.outputs = outputs
        self.buffers = {}
        self.indices = {}
        for key in outputs:
            self.buffers[key] = np.zeros((outputs[key]['size'],), dtype=outputs[key]['dtype'])
            self.indices[key] = 0
    
    def push(**outputs):
        for key in outputs:
            i = self.indices[key] = self.indices[key] + 1
            self.buffers[key][i % self.outputs[key]['size']] = outputs[key]
            
    def plot(self):
        keys = self.outputs.keys()
        n = len(keys)
        rows = cols = np.ceil(np.sqrt(n))
        fig = plt.figure()
        for r in range(rows):
            for c in range(cols):
                i = 3 * r + c + 1
                ax = fig.add_subplot(r + 1, c + 1, i)
                ax.plot(self.buffers[keys[i]])