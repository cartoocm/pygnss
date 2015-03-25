
# block should return block of data of requested size and the block epoch

from os.path import getsize
from os import SEEK_SET
from numpy import zeros, byte, fromfile


class SignalSource:
    """
    Provides an abstract interface to digitized data from a GNSS front-end.
    The actual source might be a file, in-memory buffer from USRP, or the network.
    These interfaces should be implemented as derived classes of `SignalSource`.
    
    We can send the Channels sliced views of the buffer. These views do not copy by default.
    """
    
    def __init__(self, f_samp, f_center, buffer_size, bit_depth=8, real=False):
        self.f_samp = f_samp
        self.f_center = f_center
        self.bit_depth = bit_depth
        self.real = real
        self.buffer_size = buffer_size
        data_type = float if self.real else complex
        self.buffer = zeros((buffer_size,), dtype=data_type)
        self.buffer_start_time = 0.
        
    # abstract???
    def get(self, block_size, time=None):
        """
        If `time` is None, returns buffer start time with block at beginning of buffer
        """
        if time:
            delta = time - self.buffer_start_time
            n = round(delta * self.f_samp)
            if n < 0 or len(self.buffer) <= n:
                raise Exception('time outside of buffer range')
        else:
            n = 0
        if len(self.buffer) <= n + block_size:
            raise Exception('requested sample range extends beyond buffer sample range')
        time = n / self.f_samp
        return self.buffer[n:n + block_size], time
    
    def min_time(self):
        return self.buffer_start_time
    
    def max_time(self):
        return self.buffer_start_time + self.buffer_size / self.f_samp


class FileSignalSource(SignalSource):
    """
    Signal source that reads signal data from a file.
    
    `file_loc` is the location of the next unread btye from the file, i.e.
    the subsequent sample to the last sample in the current buffer
    """
    
    def __init__(self, filepath, f_samp, f_center, buffer_size=None, bit_depth=8, real=True):
        self.filepath = filepath
        self.file_loc = 0
        self.file_size = getsize(filepath)
        if not buffer_size:
            buffer_size = self.file_size
        super(FileSignalSource, self).__init__(f_samp, f_center, buffer_size, bit_depth, real)
    
    def load(self, overlap=0):
        '''
        Loads data from file into SignalSource buffer.
        Curent supported data formats:
        8-bit real
        4-bit complex w/ upper nibble real
        '''
        if overlap:
            self.buffer[:overlap] = self.buffer[-overlap:]
        with open(self.filepath, "rb") as f:  # reopen the file
            f.seek(self.file_loc, SEEK_SET)   # seek
            # TODO handle different bit depths and complex types
            if self.real and self.bit_depth == 8:
                self.buffer[:] = fromfile(f, dtype=byte, count=int(self.buffer_size - overlap))
            elif not self.real and self.bit_depth == 4:
                temp = fromfile(f, dtype=byte, count=int(self.buffer_size - overlap))
                # typically real is upper nibble, complex is lower nibble, but TODO make this generic
                real = temp & 0x0F
                imag = temp & 0xF0 >> 4
                real[real & 0b1000] -= 2**4
                imag[imag & 0b1000] -= 2**4
                self.buffer[:] = real + 1j * imag
            
    def advance(self, overlap=100000):
        # TODO handle overlap and buffer size incompatibilities?
        self.file_loc += self.buffer_size - overlap
        self.load(overlap)
        