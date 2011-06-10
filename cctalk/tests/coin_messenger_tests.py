from .. coin_messenger import CoinMessenger
from .. import tools
from . tools_tests import test_get_tty_port

def test_creation():
    cf = 'test_creation'
    port_type = 'coin_validator'
    
    test_get_tty_port(port_type, calling_fn=cf)

    so = tools.make_serial_object(port_type)
    cm = CoinMessenger(so)
