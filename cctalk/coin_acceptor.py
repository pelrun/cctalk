import numpy
import time

from struct import pack, unpack, calcsize
from cctalk.tools import Holder, make_serial_object

def make_msg(code, data=None, to_slave_addr=2, from_host_addr=1):
    if not data:
        seq = [to_slave_addr, 0, from_host_addr, code]
    else:
        seq = [to_slave_addr, len(data), from_host_addr, code] + data
    packet = numpy.array(seq)
    end_byte = 256 - (packet.sum()%256)
    packet = packet.tolist() + [end_byte]
    return packet

def send_packet_and_get_reply(serial_object, packet_holder, initial_wait=0.05, total_wait=1,
                              debug=True, verbose=True):

    h = packet_holder
    packet = h.packet
    byte_msg = h.byte_message

    s = time.time()
    serial_object.write(packet)
    time.sleep(initial_wait)
    while True:
        t = time.time() - s
        if t > total_wait: break

        raw = serial_object.read(serial_object.inWaiting())
        if len(raw) > 1:
            len_raw = len(raw)
            out_byte = unpack('={0}c'.format(int(len_raw)), raw)
            out_int = map(ord, out_byte)

            if verbose:
                print 'Recieved original packet int: {0}   byte:{1}'.format(out_int, out_byte)
            
            if len(out_byte) == len(byte_msg) and debug:
                print 'Recieved original packet int: {0}   byte:{1}'.format(out_int, byte_msg)
            elif len(out_byte) < len(byte_msg) and debug:
                print 'Recieved small packet int: {0}   byte:{1}'.format(out_int, byte_msg)
            else:
                # The first part of the return is the echo in the line
                # (a repeat of the message sent).
                start_index = 5 + h.bytes_sent
                reply_packet = out_byte[start_index:]

                reply_msg = interpret_reply(reply_packet, packet_holder, verbose=verbose)

                if reply_msg:
                    return reply_msg
                else:
                    msg = "A bad reply was recieved."
                    raise UserWarning(msg, (reply_packet, reply_msg))
    
    return False

def interpret_reply(reply_byte, packet_holder, verbose=False):
    h = packet_holder
    reply_length = h.bytes_returned
    reply_type = h.type_returned
    reply_int = map(ord, reply_byte)

    if len(reply_int) < 2:
        print 'Recieved small packet int: {0}   byte:{1}'.format(reply_int, reply_byte)
        return False

    msg_length = reply_int[1]
    if verbose:
        print "Recieved {0} bytes:".format(msg_length)

    if msg_length != reply_length:
        print 'Message length != return_length.  ml: {0}   rl:{1}'.format(msg_length, reply_length)
        return False


    if h.request_code == 254:
        expected_reply = [1, 0, 2, 0, 253]
        if reply_int != expected_reply:
            msg = "Simple pool did not return expected message."
            raise UserWarning(msg, (reply_int, expected_reply))

    reply_msg_int = reply_int[4:-1]
    reply_msg_byte = reply_byte[4:-1]
    
    if reply_type is str:
        return str().join(reply_msg_byte)
    elif reply_type is int:
        return reply_msg_int
    elif reply_type is bool:
        return True
    else:
        return reply_msg_byte

class CoinMessanger(object):
    r_info = dict(reset_device=(1, 0, bool),
                  comms_revision=(4, 3, int),              # Expected: 2, 4, 2
                  request_build_code=(192, 3, str),
                  data_storage_availability=(216, 5, int),
                  read_buffered_credit_or_error_codes=(229, 11, int),
                  master_inhibit_status=(227, 1, int),
                  inhibit_status=(230, 2, int),
                  software_revision=(241, 5, str),         # Expected: 52.05
                  serial_number=(242, 3, int),
                  product_type=(244, 3, str),              # Expected: G13
                  equiptment_category=(245, 13, str),      # Expected: Coin Acceptor
                  manufacturer_ID=(246, 3, str),           # Expected: NRI   Gets NR with I as checksum.
                  simple_poll=(254, 0, bool),
                  )

    
    def __init__(self, serial_object):
        self.serial_object = serial_object
        self.request_data = {}
        for k, v in self.r_info.items():
            int_msg = make_msg(v[0])
            byte_msg = map(chr, int_msg)
            packet = pack('=ccccc', *byte_msg)

            self.request_data[k] = Holder(dict(packet=packet,
                                               integer_message=int_msg,
                                               byte_message=byte_msg,
                                               request_code=v[0],
                                               bytes_returned=v[1],
                                               bytes_sent=0,
                                               type_returned=v[2],
                                               user_message=k,
                                               ))

    def accept_coins(self, state=None, verbose=False):
        if state is None:
            state = True

        if not state and state != False:
            msg = 'The state must be either True or False.'
            raise UserWarning(msg, (state))

        if state:
            s_msg = 'on'
        else:
            s_msg = 'off'
            
        int_msg = make_msg(231, [255, 255])
        byte_msg = map(chr, int_msg)
        packet = pack('=ccccccc', *byte_msg)

        if not self.serial_object.isOpen():
            msg = "The serial_object.isOpen() is False."
            raise UserWarning(msg, (self.serial_object.isOpen()))

        ph = Holder(dict(packet=packet,
                         integer_message=int_msg,
                         byte_message=byte_msg,
                         request_code=231,
                         bytes_returned=0,
                         bytes_sent=2,
                         type_returned=bool,
                         user_message='modify_inhibit_status_{0}'.format(s_msg),
                         ))
        #print 'Requesting: {0}'.format(ph.user_message)
        #if verbose:
        #    print 'Sending   int_msg: {0}   byte_msg: {1}'.format(ph.integer_message, ph.byte_message)
        reply_msg = send_packet_and_get_reply(self.serial_object, ph, verbose=verbose)
        #print reply_msg

    def set_accept_limit(self, coins=1, verbose=False):

        if type(coins) != type(int()):
            msg = 'The number of coins must be an integer.'
            raise UserWarning(msg, (coins, type(coins)))

        int_msg = make_msg(135, [coins])
        byte_msg = map(chr, int_msg)
        packet = pack('=cccccc', *byte_msg)

        if not self.serial_object.isOpen():
            msg = "The serial_object.isOpen() is False."
            raise UserWarning(msg, (self.serial_object.isOpen()))

        ph = Holder(dict(packet=packet,
                         integer_message=int_msg,
                         byte_message=byte_msg,
                         request_code=135,
                         bytes_returned=0,
                         bytes_sent=1,
                         type_returned=bool,
                         user_message='set_accept_limit_{0}'.format(coins),
                         ))
        print 'Requesting: {0}'.format(ph.user_message)
        if verbose:
            print 'Sending   int_msg: {0}   byte_msg: {1}'.format(ph.integer_message, ph.byte_message)
        reply_msg = send_packet_and_get_reply(self.serial_object, ph, verbose=verbose)
        print reply_msg

    def read_buffer(self):
        return self.request('read_buffered_credit_or_error_codes')

    def get_coin_id(self, slot, verbose=False):
        int_msg = make_msg(184, [slot])
        byte_msg = map(chr, int_msg)
        packet = pack('=cccccc', *byte_msg)

        if not self.serial_object.isOpen():
            msg = "The serial_object.isOpen() is False."
            raise UserWarning(msg, (self.serial_object.isOpen()))

        ph = Holder(dict(packet=packet,
                         integer_message=int_msg,
                         byte_message=byte_msg,
                         request_code=184,
                         bytes_returned=6,
                         bytes_sent=1,
                         type_returned=str,
                         user_message='get_coin_id_{0}'.format(slot),
                         ))
        print 'Requesting: {0}'.format(ph.user_message)
        if verbose:
            print 'Sending   int_msg: {0}   byte_msg: {1}'.format(ph.integer_message, ph.byte_message)
        reply_msg = send_packet_and_get_reply(self.serial_object, ph, verbose=verbose)
        print reply_msg

    def request(self, request_key, verbose=False):
        r_dic = self.request_data.get(request_key, None)
        if not r_dic:
            msg = 'This request_key has not been implimented.'
            raise NotImplimentedError(msg, (request_key))

        if not self.serial_object.isOpen():
            msg = "The serial_object.isOpen() is False."
            raise UserWarning(msg, (self.serial_object.isOpen()))
        
        #print 'Requesting: {0}'.format(r_dic.user_message)
        if verbose:
            print 'Sending   int_msg: {0}   byte_msg: {1}'.format(r_dic.integer_message, r_dic.byte_message)
        reply_msg = send_packet_and_get_reply(self.serial_object, r_dic, verbose=verbose)

        return reply_msg
            

if __name__ == '__main__':
    coin_validator_connection = make_serial_object('coin_validator')
    coin_validator_connection.open()
    coin_messanger = CoinMessanger(coin_validator_connection)

    #for i in range(1,17):
    #    coin_messanger.get_coin_id(i)
        
    coin_messanger.read_buffer()
    coin_messanger.accept_coins(True)

    #coin_messanger.request('reset_device', verbose=True)
    #coin_messanger.request('data_storage_availability', verbose=True)
    
    coin_messanger.read_buffer()
    coin_messanger.set_accept_limit(25)
    
    s = time.time()
    while True:
        coin_messanger.accept_coins(True)
        data_buffer = coin_messanger.read_buffer()
        print data_buffer
        time.sleep(0.2)

        if time.time() - s > 40:
            break
