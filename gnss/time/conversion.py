"""
Utilities for doing GNSS time conversions.
"""

__author__ = "Brian Breitsch"
__copyright__ = "Copyright 2014"
__credits__ = ["Brian Breitsch"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Brian Breitsch"
__email__ = "brianbreitsch@gmail.com"
__status__ = "Infant"

from numpy import modf
from datetime import datetime, timedelta
from pytz import UTC
try:
    from urllib.request import urlretrieve  # python 3
except ImportError:
    from urllib2 import urlretrieve  # python 2
from os.path import isfile, dirname, join
from collections import namedtuple

OffsetEpoch = namedtuple('OffsetEpoch', ['epoch', 'offset'])

NTP_EPOCH = datetime(year=1900, month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC)
GPS_EPOCH = datetime(year=1980, month=1, day=6, hour=0, minute=0, second=0, tzinfo=UTC)
SECONDS_IN_WEEK = 60 * 60 * 24 * 7
LEAP_SECOND_EPOCHS = []

def download_tai_leap_seconds(filepath):
    leap_seconds_list_url = 'http://www.ietf.org/timezones/data/leap-seconds.list'
    leap_seconds_data = urlretrieve(leap_seconds_list_url, filepath)

def parse_tai_leap_seconds(filepath):
    with open(filepath, 'r') as leap_seconds_data:
        for line in leap_seconds_data.readlines():
            line = line.decode('utf-8') if type(line) == type(b'a') else line
            if line.startswith("#$"):
                file_update_ntp = int(line.split()[1])
            elif line.startswith("#@"):
                file_expiration_ntp = int(line.split()[1])
            elif line.startswith("#") or line == "":
                # if line is comment or blank, ignore
                continue
            else:
                ntp_timestamp = int(line.split()[0])
                offset = int(line.split()[1])
                epoch = NTP_EPOCH + timedelta(seconds=ntp_timestamp)
                LEAP_SECOND_EPOCHS.append(OffsetEpoch(epoch, offset))

# need to download/parse leap second epochs if not already done
_leap_seconds_file = join(dirname(__file__), './leap_second_epochs.txt')
if not LEAP_SECOND_EPOCHS:
    if not isfile(_leap_seconds_file):
        download_tai_leap_seconds(_leap_seconds_file)
        print('downloaded leap seconds file')
    parse_tai_leap_seconds(_leap_seconds_file)
    print('there are {0} leap second epochs'.format(len(LEAP_SECOND_EPOCHS)))

def utc_tai_offset(time):
    """
    Calculates the offset (number of leap seconds) between a
    given time and TAI. If `time` is before the first leap
    seconds were introduced in 1972, returns 10--which is the
    original offset introduced in 1972. Otherwise, returns 
    the offset corresponding to the last offset before
    `time`.
    
    input
    -----
    time: datetime
        the time for which to find leap seconds
    
    output
    ------
    offset: timedelta
        the total leap second offset
    """
    for i in range(len(LEAP_SECOND_EPOCHS)):
        if LEAP_SECOND_EPOCHS[i].epoch > time:
            offset = LEAP_SECOND_EPOCHS[i-1].offset if i > 0 else LEAP_SECOND_EPOCHS[0].offset
            return timedelta(seconds=offset)
    return timedelta(seconds=LEAP_SECOND_EPOCHS[-1].offset)

class gpstime:
    """
    Creates `gpstime` from `datetime` object.
    GPS time is specified any of the following:
     - total seconds (without leap) since GPS epoch
     - week number and day of week
     - week number and seconds into week
    """
    
    gps_tai_offset = utc_tai_offset(GPS_EPOCH)
    
    def __init__(self, time):
        """
        input
        -----
        time: datetime
            the time to convert to GPS time
        """
        time_gps_offset = utc_tai_offset(time) - self.gps_tai_offset
        self.leap_second_offset = time_gps_offset
        self.timedelta = time - GPS_EPOCH + time_gps_offset

    @property
    def gps_seconds(self):
        "Returns time in GPS seconds"
        return self.timedelta.total_seconds()

    @property
    def week_and_dow(self):
        "Returns GPS week number and day of the week"
        frac_week, week = modf(self.timedelta.total_seconds() / SECONDS_IN_WEEK)
        return int(week), frac_week * 7
    
    @property
    def week_and_week_seconds(self):
        "Returns GPS week number and seconds into week"
        frac_week, week = modf(self.timedelta.total_seconds() / SECONDS_IN_WEEK)
        return int(week), round(frac_week * 7 * 24 * 60 * 60)

    
def utctime(seconds, week_no=None):
    """
    Returns a UTC datetime object given the GPS week
    number and/or number of seconds.

    input
    -----
    seconds: float
        if `seconds` is the only argument (i.e. `week_no` is
        `None`) then it is taken to be the total number of
        seconds since the GPS epoch on 6 January 1980.
        Otherwise, it is the number of seconds plus 
        fractional seconds since the last GPS week epoch
    week_no: int
        GPS week number

    output
    ------
    utctime: datetime
        the UTC datetime object corresponding to the GPS
        time input
    """
    total_seconds = seconds + week_no * SECONDS_IN_WEEK if week_no else seconds
    ## TODO this is a tricky function
    time = GPS_EPOCH + timedelta(seconds=total_seconds)
    return time + gpstime.gps_tai_offset - utc_tai_offset(time)
