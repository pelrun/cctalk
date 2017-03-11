""" Provides the CoinMessenger class definition.

Module content
--------------
"""
# The python-cctalk package allows one to send ccTalk messages and decode replies from a coin validator. 
license_text = "(C) 2011 David Schryer GNU GPLv3 or later."
__copyright__ = license_text

__autodoc__ = ['CoinMessenger']
__all__ = __autodoc__

import time

from . tools import make_serial_object, make_msg, send_message_and_get_reply

def log(message, verbose=False):
    if verbose:
        print 'Requesting: {0}'.format(message['user_message'])

class CoinMessenger(object):
    """This is an object used to talk with ccTalk coin validators.

    It provides functions for requesting and recieving data as
    well as changing the state of the coin validator.
    """
    
    r_info = dict(reset_device=(1, 0, bool),
                  comms_revision=(4, 3, int),              # Expected: 2, 4, 2
                  alarm_counter=(176,1,int),
                  bank_select=(178,1,int),
                  build_code=(192, -1, str),
                  reject_counter=(193,3,int),
                  fraud_counter=(194,3,int),
                  teach_status=(201,2,int),
                  option_flags=(213,1,int),
                  data_storage_availability=(216, 5, int),
                  accept_counter=(225,3,int),
                  insertion_counter=(226,3,int),
                  master_inhibit_status=(227, 1, int),
                  read_buffered_credit_or_error_codes=(229, 11, int),
                  inhibit_status=(230, 2, int),
                  perform_self_check=(232,-1,int),
                  software_revision=(241, -1, str),
                  serial_number=(242, 3, int),
                  database_version=(243, 1, int),
                  product_type=(244, -1, str),
                  equipment_category=(245, -1, str),      # Expected: Coin Acceptor
                  manufacturer_ID=(246, -1, str),
                  variable_set=(247, -1, int),
                  polling_priority=(249, 2, int),
                  simple_poll=(254, 0, bool),
                  )

    
    def __init__(self, serial_object, verbose = False):
        self.serial_object = serial_object
        self.request_data = {}
	self.verbose = verbose
        for k, v in self.r_info.items():
            self.request_data[k] = dict(message=make_msg(v[0]),
                                        request_code=v[0],
                                        bytes_expected=v[1],
                                        bytes_sent=0,
                                        type_returned=v[2],
                                        user_message=k,
                                        )

    def accept_coins(self, mask=[255,255]):
        """Change accept coin state.

        Parameters
        ----------
        state : bool
          State to change the coin validator too.

        Raises
        ------
        UserWarning
          -- If the state is not True or False.
          -- If self.serial_object.isOpen() is False.
        """

        if len(mask) != 2:
            msg = "accept_coins mask must be a 2-ple."
            raise UserWarning(msg, (self.serial_object.isOpen()))

        ph = dict(message=make_msg(231, mask),
                  request_code=231,
                  bytes_expected=0,
                  bytes_sent=2,
                  type_returned=bool,
                  user_message='modify_inhibit_status_{0}'.format(mask),
                  )

	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def master_inhibit(self, state=True):
        """Change master inhibit state.

        Parameters
        ----------
        state : bool
          State to change the coin validator too.

        Raises
        ------
        UserWarning
          -- If the state is not True or False.
          -- If self.serial_object.isOpen() is False.
        """
        if state:
            param = 0
        else:
            param = 1
 
        ph = dict(message=make_msg(228, [param]),
                  request_code=228,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='modify_master_inhibit_status_{0}'.format(state),
                  )
	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def set_accept_limit(self, coins=1):
        """Sets the accept limit of the coin validator.

        Parameters
        ----------
        coins : int
          Number of coins.  Defaults to 1.
        """
        if type(coins) != type(int()):
            msg = 'The number of coins must be an integer.'
            raise UserWarning(msg, (coins, type(coins)))

        ph = dict(message=make_msg(135, [coins]),
                  request_code=135,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='set_accept_limit_{0}'.format(coins),
                  )
	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        print reply_msg

    def read_buffer(self):
        """Shortcut for self.request('read_buffered_credit_or_error_codes')

        Returns
        -------
        output : output from self.request('read_buffered_credit_or_error_codes')
        """
        return self.request('read_buffered_credit_or_error_codes')

    def get_coin_id(self, slot):
        """Prints out the coin id for a slot number.

        Parameters
        ----------
        slot : int
          Slot number.
        """
        ph = dict(message=make_msg(184, [slot]),
                  request_code=184,
                  bytes_expected=6,
                  bytes_sent=1,
                  type_returned=str,
                  user_message='get_coin_id_{0}'.format(slot),
                  )
	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def modify_coin_id(self, slot, text):
        """Change the coin id for a slot number.

        Parameters
        ----------
        slot : int
          Slot number.
        """

	text_raw = map(ord,'{:.<6}'.format(text))
        ph = dict(message=make_msg(185, [slot] + text_raw),
                  request_code=185,
                  bytes_expected=0,
                  bytes_sent=7,
                  type_returned=bool,
                  user_message='modify_coin_id_{0}_{1}'.format(slot,text),
                  )
	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def teach_mode_control(self, slot):
        ph = dict(message=make_msg(202, [slot]),
                  request_code=202,
                  bytes_expected=0,
                  bytes_sent=1,
                  type_returned=bool,
                  user_message='teach_mode_control_{0}'.format(slot),
                  )
	log(ph, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, ph, verbose=self.verbose)
        return reply_msg

    def request(self, request_key):
        """Requests messages programmed into the request Holder in __init__.

        Parameters
        ----------
        request_key : key
          Key in the request Holder.

        Returns
        -------
        reply_msg : reply message from :py:func:`cctalk.tools.send_message_and_get_reply`

        Raises
        ------
        NotImplimentedError
          If the key is not in the request Holder.
        UserWarning
          If self.serial_object.isOpen() is False
        """
        r_dic = self.request_data.get(request_key, None)
        if not r_dic:
            msg = 'This request_key has not been implemented.'
            raise NotImplementedError(msg, (request_key))

        log(r_dic, verbose=self.verbose)
        reply_msg = send_message_and_get_reply(self.serial_object, r_dic, verbose=self.verbose)

        return reply_msg
        
