

from gnss.codes import gps_l1, gps_l2, gps_l5

GPSL1_CARRIER_FREQUENCY = 1.57542e9
GPSL2_CARRIER_FREQUENCY = 1.2276e9
GPSL5_CARRIER_FREQUENCY = 1.17645e9

class Signal:
    """
    Defines attributes of a GNSS signal, which is comprised of one code modulated on one carrier frequency.
    
    
    -8 is unkown GLONASS frequency number.
    """
    
    def __init__(self, svid, f_carrier, code, f_nav=None, code_nav=None, signal_type='', freq_no=-8):
        self.f_carrier = f_carrier
        self.code = code
        self.f_nav = f_nav
        self.code_nav = code_nav
        self.signal_type = signal_type
    
    def GPSL1CA(svid):
        code = gps_l1.gps_l1ca(svid)
        return Signal(svid, GPSL1_CARRIER_FREQUENCY, code, 50., signal_type='GPSL1CA')
    
    def GPSL2(svid):
        code = gps_l2.gps_l2c(svid)
        return Signal(svid, GPSL2_CARRIER_FREQUENCY, code, signal_type='GPSL2C')
      
    def GPSL5_I(svid):
        code_i = gps_l5.gps_l5i(svid)
        return Signal(svid, GPSL5_CARRIER_FREQUENCY, code_i, signal_type='GPSL5I')
    
    def GPSL5_Q(svid):
        # TODO describe nav data
        code_q = gps_l5.gps_l5q(svid)
        return Signal(svid, GPSL5_CARRIER_FREQUENCY, code_q, signal_type='GPSL5Q')
    