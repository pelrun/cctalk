""" Provides tools for general use.

Module content
--------------
"""
# The python-cctalk package allows one to send ccTalk messages and decode replies from a coin validator. 
license_text = "(C) 2011 David Schryer GNU GPLv3 or later."
__copyright__ = license_text

__autodoc__ = ['make_serial_object', 'drop_to_ipython', 'make_msg', 'send_message_and_get_reply', 'interpret_reply']
__all__ = __autodoc__

from IPython.terminal.embed import InteractiveShellEmbed

import os
import serial
import time
import subprocess
from struct import unpack

def make_msg(code, data=None, to_slave_addr=2, from_host_addr=1):
    """Makes a ccTalk message from a ccTalk code and data to be sent with this message.

    Parameters
    ----------
    code : int
      ccTalk code for this message.
    data : list of integers
      Data to be sent in this message.
    to_slave_addr : int
      Address of slave to be sent to.  Defaults to 2.
    from_host_addr : int
      Address of host that is sending the message.  Defaults to 1.

    Returns
    -------
    message : list of integers
      An integer equivalent of the ccTalk message.
      This needs to be converted to a byte message prior to sending.
    """
    if not data:
        seq = [to_slave_addr, 0, from_host_addr, code]
    else:
        seq = [to_slave_addr, len(data), from_host_addr, code] + data
    message_sum = 0
    for i in seq:
        message_sum += i
    end_byte = 256 - (message_sum%256)
    message = seq + [end_byte]
    return message

def read_message(serial_object):
    serial_object.timeout = 1
    serial_object.inter_byte_timeout = 0.1 # should be 0.05 but linux doesn't support it

    header = serial_object.read(4)
    if len(header)<4:
        return False

    # header: destination, length, source, message_id

    message_length = ord(header[1])+1
    body = serial_object.read(message_length)

    if len(body)<message_length:
        return False

    reply = list(map(ord,header+body))

    # TODO: check checksum

    return reply


def send_message_and_get_reply(serial_object, message, verbose=False):
    """Sends a message and gets a reply.

    Parameters
    ----------
    serial_object : object made with :py:func:`cctalk.tools.make_serial_object`
      Serial communication object.
    message : Holder
      Holder containing the message and extended information about the message being send.
      See :py:class:`cctalk.coin_messenger.CoinMessenger` for Holder construction.
    verbose : bool
      Flag to be more verbose.

    Returns
    -------
    reply_msg : message recieved from :py:func:`cctalk.tools.interpret_reply`
      if reply_msg is False, no reply was obtained.

    Raises
    ------
    UserWarning
      If a reply was obtained but :py:func:`cctalk.tools.interpret_reply` returned False.
    """

    if not serial_object.isOpen():
        msg = 'The serial port is not open.'
        raise UserWarning(msg, (serial_object.isOpen()))

    packet = ''.join(map(chr,message['message']))
    serial_object.reset_input_buffer()
    serial_object.reset_output_buffer()

    serial_object.write(packet)

    output = read_message(serial_object)
    reply = read_message(serial_object)

    if not reply or reply[0] != 1:
        return False 

    reply_length = reply[1]
    expected_length = message['bytes_expected']
    reply_type = message['type_returned']

    if len(reply) < 2:
        print('Recieved small message: {0}'.format(reply))
        return False

    if verbose:
        print("Recieved {0} bytes:".format(msg_length))

    if expected_length != -1 and reply_length != expected_length:
        print('Expected {1} bytes but received {0}'.format(reply_length, expected_length))
        return False

    reply_data = reply[4:-1]
    
    if reply_type is str:
        return str().join(map(chr,reply_data))
    elif reply_type is int:
        return reply_data
    elif reply_type is bool:
        return True
    else:
        return list(map(chr,reply))

def make_serial_object(tty_port):
    """Makes a serial object that can be used for talking with the coin validator.

    port_type is a string that can currently only be equal to 'coin_validator'.

    Paramters
    ---------
    port_type : str
      Type of port to connect to.  Currently only 'coin_validator is valid.'

    Returns
    -------
    serial_object : object made by :py:class:`serial.Serial`
    """
    
    return serial.Serial(port=tty_port,
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS,
                         xonxoff=True,
                         )

def drop_to_ipython(local_variables, *variables_to_inspect):
    '''
    Drops to ipython at the point in the code where it is called to inspect the variables passed to it.

    Parameters
    ----------
    local_variables : list
      Usually one would pass the output of locals().
    variables_to_inspect: tuple
      All variables passed to this routine are wrapped into a tuple.
    '''

    try:
        call_name = local_variables['self'].__module__
    except Exception:
        call_name = "Module"

    b = 'Dropping into IPython'
    em = 'Leaving Interpreter, back to program.'
    msg = '***Called from %s. Hit Ctrl-D to exit interpreter and continue program.'
    ipshell = InteractiveShellEmbed([], banner1=b, exit_msg=em)
    ipshell(msg %(call_name))

