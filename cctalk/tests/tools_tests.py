from .. import tools

def test_get_tty_port(port_type=None, calling_fn=None):

    if port_type is None:
        port_type = 'coin_validator'
    if calling_fn is None:
        msg = 'The tty port for {0} was not found.'.format(port_type)
    else:
        msg = 'Cannot test {0} since no tty_port was found. Error: {1}'
        
    try:
        tty_port = tools._get_tty_port(port_type)
    except Exception as e:
        raise AssertionError(msg.format(calling_fn, e))


def test_make_serial_object():
    cf = 'test_make_serial_object'
    
    for port_type in ['coin_validator']:
        test_get_tty_port(port_type, calling_fn=cf)
        so = tools.make_serial_object(port_type)

def test_make_msg():
    
    int_msg = tools.make_msg(231, [255, 255])

    if int_msg != [2, 2, 1, 231, 255, 255, 22]:
        msg = "Did not compose expected message."
        raise AssertionError(msg, (int_msg))
