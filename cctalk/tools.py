""" Provides tools for general use.

Module content
--------------
"""
# Author: David Schryer
# Created: 2011

__autodoc__ = ['Holder', 'make_serial_object', 'drop_to_ipython']

__all__ = __autodoc__

from IPython.Shell import IPShellEmbed

import os
import serial
import subprocess

def _get_tty_port(port_type):
    '''
    Returns the tty device name for either 'camera_relay' or 'coin_validator'.

    Only used within this module.
    '''
    if port_type == 'camera_relay':
        usb_conn = '3-3'
    elif port_type == 'coin_validator':
        usb_conn = '3-2'

    cmd = 'lshal |grep sysfs | grep ttyUSB | grep {0}'.format(usb_conn)

    cmd_proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                env=os.environ)
    cmd_out, cmd_err = cmd_proc.communicate()

    out_string = cmd_out.split('/tty/')
    if len(out_string) != 2:
        msg = "No USB device {0} was found ({1}).  Look at: lshal |grep sysfs | grep ttyUSB".format(usb_conn, port_type)
        raise UserWarning(msg, (cmd_out))

    return out_string[1].split("'")[0]


def make_serial_object(port_type):
    '''
    Makes a serial object that can be used for talking with either the relay or coin validator.

    port_type is a string that is either 'camera_relay' or 'coin_validator'.
    '''
    tty_port = _get_tty_port(port_type)
    return serial.Serial(port="/dev/{0}".format(tty_port),
                         baudrate=9600,
                         parity=serial.PARITY_NONE,
                         stopbits=serial.STOPBITS_ONE,
                         bytesize=serial.EIGHTBITS,
                         xonxoff=True,
                         )

def drop_to_ipython(*z, **kwds):
    '''
    Drops to ipython at the point in the code where it is called to inspect the variables passed to it.

    Parameters
    ----------
    z: tuple
      All variables passed to this routine are wrapped into a tuple.
    kwds : dict
      If the keyword "local_variables" is passed (output of locals()),
      the call name is extracted from the calling class.
    '''
    lvs = kwds.get('local_variables', False) 
    if not lvs:
        lvs = []
        
    try:
        call_name = local_variables['self'].__module__
    except Exception:
        call_name = "Module"

    b = 'Dropping into IPython'
    em = 'Leaving Interpreter, back to program.'
    msg = '***Called from %s. Hit Ctrl-D to exit interpreter and continue program.'
    ipshell = IPShellEmbed([], banner=b, exit_msg=em)
    ipshell(msg %(call_name))


class Holder(object):
    """This is a loose implimentation of  a dictionary object.

    It gives access to its items as member variables of a class.
    """
    def __init__(self, item=None):

        if item:
            self.add(item)

    def add(self, item):

        if isinstance(item, dict):
            self.__dict__.update(item)
            
        elif isinstance(item, Holder):
            self.__dict__.update(item.__dict__)
            
        else:
            msg = "This Holder only supports dictionaries and other Holder objects."
            raise UserWarning(msg, (item, type(item)))

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get(self, key, alternate=None):
        return self.__dict__.get(key, alternate)

    def has_key(self, key):
        return self.__dict__.has_key(key)

    def keys(self):
        return self.__dict__.keys()
    
    def items(self):
        return self.__dict__.items()
    
    def values(self):
        return self.__dict__.values()
