

class ChannelController:
    """
    At a given time, a `ChannelController` object is focused on a particular time range
    of data for a particular signal. It can tell any of its registered Channels to process 
    this segment of data. The data resides inside a `SignalBuffer` object, while information
    about the data format resides inside the `SignalSource` object
    """
    
    def __init__(self, signal_source):
        self.signal_source = signal_source
        self.signal_buffer = signal_buffer
    
    def add_channel(self, channel):
        self.channels.append(channel)
        