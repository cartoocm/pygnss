

class SatChannel:
    """
    Keeps track of tracking status for a single GNSS satellite.
    `SignalChannel` objects are childs of their corresponding `SatChannel` objects.
    """
    
    def __init__(self, svid):
        self.svid = svid
        self.channels = []
    
    def register_signal_channel(self, channel):
        self.channels.append(channel)
    
    def process(self, time, data):
        for channel in self.channels:
            channel.process(time, data)
            
            
class SignalChannel:
    """
    Keeps track of acquisition and tracking states for a single GNSS signal.
    """
    
    def __init__(self, signal):
        self.signal = signal
    
    def process(self, time, data):
        if self.state is 'TRACK':
            self.track(time, data)
        elif self.state is 'ACQUIRE':
            self.acquire(time, data)
        else:  # state is to do nothing
            pass
    
    def acquire(self, time, data):
        # check how accurate our acquisition is, then act accordingly
        pass
    
    def track(self, time, data):
        # check if we're moving forward or backward, propagate to `time`, and perform tracking algorithm
        pass