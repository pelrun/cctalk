from .. coin_messenger import CoinMessenger
from .. import tools
from . tools_tests import test_get_tty_port

def test_creation():

    tty_port = test_get_tty_port('coin_validator')
    so = tools.make_serial_object(tty_port)
    cm = CoinMessenger(so)
