
# block should return block of data of requested size and the block epoch

from os.path import getsize
from os import SEEK_SET
from numpy import zeros, byte, fromfile, uint8, int8, bitwise_and, s_, concatenate, delete


class Source:
    """
    Provides an abstract interface to digitized data from a GNSS front-end.
    The actual source might be a file, in-memory buffer from USRP, or the network.
    These interfaces should be implemented as derived classes of `Source`.
    
    We can send the Channels sliced views of the buffer. These views do not copy by default.
    
    `decimation` specifies by how much to decimate incoming data. If not 1 (default)
    takes every nth sample to store in buffer, where n is the value of decimate
    """
    
    MAX_BUFFER_SIZE = 100000000  # 100 MSamples
    
    def __init__(self, source_f_samp, source_f_center, buffer_size, bit_depth, real, decimation=1):
        self.source_f_samp = source_f_samp
        self.decimation = decimation
        self.f_samp = source_f_samp / decimation
        self.f_center = source_f_center
        self.bit_depth = bit_depth    # bits per sample component (8 bits total for real+imaginary)
        self.real = real
        if buffer_size > Source.MAX_BUFFER_SIZE:
            raise Error('`buffer_size` exceeds `MAX_BUFFER_SIZE`')
        self.buffer_size = buffer_size
        data_type = float if self.real else complex
        self.bytes_per_sample = self.bit_depth / 8 if self.real else self.bit_depth / 4
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
    
    @property
    def min_time(self):
        return self.buffer_start_time
    
    @property
    def max_time(self):
        return self.buffer_start_time + self.buffer_size / self.f_samp
    
    def decimate(self, samples):
        '''
        Performs simple decimation by taking every nth sample, where n
        is the value of `decimate`
        '''
        return samples[::self.decimation]
    
    def convert_to_complex_samples(self, byte_arr):
        '''
        Generic parsing of complex samples.
        Handles 4-bit case
        `samples` is a byte array 
        TODO add others?
        Throws error if `self.bit_depth` is unsupported.
        '''
        # typically real is upper nibble, complex is lower nibble, but TODO make this generic
        if self.bit_depth == 4:
            real = (bitwise_and(byte_arr, 0x0f) << 4).astype(int8) >> 4
            imag = bitwise_and(byte_arr, 0xf0).astype(int8) >> 4
        elif self.bit_depth == 8:
            real = byte_arr[0::2]  # TODO this might not be working
            imag = byte_arr[1::2]
        else:
            raise Error('Bit depth not supported for complex samples')
        return real + 1j * imag


class FileSource(Source):
    """
    Signal source that reads signal data from a file.
    
    `file_loc` is the location of the next unread btye from the file, i.e.
    the subsequent sample to the last sample in the current buffer
    
    """
    
    def __init__(self, filepath, file_f_samp, f_center, bit_depth, real, buffer_size=None, decimation=1):
        self.filepath = filepath
        self.file_loc = 0
        self.file_size = getsize(filepath)
        if not buffer_size:
            buffer_size = self.file_size
        super(FileSource, self).__init__(file_f_samp, f_center, buffer_size, bit_depth, real, decimation)

    def load(self, overlap=0):
        '''
        Loads data from file into Source buffer.
        '''
        if overlap:
            self.buffer[:overlap] = self.buffer[-overlap:]
        with open(self.filepath, "rb") as f:  # reopen the file
            f.seek(self.file_loc, SEEK_SET)   # seek
            samples_to_read = self.decimation * (self.buffer_size - overlap)
            bytes_to_read = samples_to_read * self.bytes_per_sample
            temp = fromfile(f, dtype=byte, count=int(bytes_to_read))
            if not self.real:
                temp = self.convert_to_complex_samples(temp)
            if self.decimation > 1:
                temp = self.decimate(temp)
            self.buffer[overlap:] = temp
            
    def advance(self, overlap=100000):
        '''
        Advances file offset to next buffer length of data in file, overlapping
        previous buffer by `overlap` samples.
        '''
        # TODO handle overlap and buffer size incompatibilities?
        self.file_loc += self.buffer_size - overlap  #TODO THIS IS WRONG
        self.buffer_start_time += (self.buffer_size - overlap) / self.f_samp
        self.load(overlap)

        
class FileSource4BitComplexWithMetaData(FileSource):
    
    def __init__(self, filepath, file_f_samp, f_center, buffer_size=None, decimation=1):
        
        super(FileSource4BitComplexWithMetaData, self).__init__(filepath, file_f_samp, f_center,
                                            buffer_size=buffer_size, bit_depth=4, real=False, decimation=decimation)
        
        self.header_size = 21    # bytes
        self.header_rate = 1000  # Hz
        
        self.bytes_per_data_segment = self.source_f_samp / self.header_rate * self.bytes_per_sample
        self.bytes_per_header_epoch = self.header_size + self.bytes_per_data_segment
        
    def load(self, overlap=0):
        '''
        Loads data from file into Source buffer.
        
        NOTE: simplification made under assumption that file_loc is never
        left in the middle of a header.
        '''
        if overlap:
            self.buffer[:overlap] = self.buffer[-overlap:]
        with open(self.filepath, "rb") as f:  # reopen the file
            f.seek(self.file_loc, SEEK_SET)   # seek

            samples_to_read = self.decimation * (self.buffer_size - overlap)
            bytes_to_read = samples_to_read * self.bytes_per_sample
            
            first_epoch_index = self.file_loc % self.bytes_per_header_epoch
            bytes_to_read_counter = bytes_to_read
            bytes_to_read_counter -= first_epoch_index  # account for front bytes
            while bytes_to_read_counter >= self.bytes_per_data_segment:  # for each header epoch read, account for header size in bytes read
                bytes_to_read_counter -= self.bytes_per_data_segment
                bytes_to_read += self.header_size
            
            temp = fromfile(f, dtype=byte, count=int(bytes_to_read))
            
            num_full_epochs = (bytes_to_read - first_epoch_index) // self.bytes_per_header_epoch
            last_epoch_index = first_epoch_index + num_full_epochs * self.bytes_per_header_epoch
            first_sample_index = max(0, first_epoch_index - self.bytes_per_data_segment)
            temp = concatenate(
                (temp[first_sample_index:first_epoch_index],
                 delete(temp[first_epoch_index:last_epoch_index].reshape((num_full_epochs, self.bytes_per_header_epoch)), s_[:self.header_size], 1).flatten(),
                 temp[last_epoch_index + self.header_size:]))
            
            if not self.real:
                temp = self.convert_to_complex_samples(temp)
            if self.decimation > 1:
                temp = self.decimate(temp)
            self.buffer[overlap:] = temp