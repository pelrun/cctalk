from .. coin_messenger import CoinMessenger
from .. import tools

def test_creation():
    cf = 'test_creation'
    port_type = '/dev/ttyS0'
    
    so = tools.make_serial_object(port_type)
    cm = CoinMessenger(so)
