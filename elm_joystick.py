import sys

import uinput
from elm327 import ELM327
from mrcrowbar import models as mrc


class Steering( mrc.Block ):
    axis = mrc.UInt16_BE( 0x00 )


class Accelerator( mrc.Block ):
    axis = mrc.UInt8( 0x06 )


class Brake( mrc.Block ):
    button = mrc.Bits( 0x03, 0b01000000 )


class Cruise( mrc.Block ):
    button = mrc.Bits( 0x00, 0b10000000 )


class Controls( mrc.Block ):
    driver_door =   mrc.Bits( 0x00, 0b10000000 )
    high_beams =    mrc.Bits( 0x03, 0b01000000 )


class Mazda3:
    def __init__( self ):
        # create a new virtual joystick device with the features we need 
        self.device = uinput.Device([
            uinput.ABS_WHEEL,
            uinput.ABS_GAS,
            uinput.BTN_0,
            uinput.BTN_1,
            uinput.BTN_2
            uinput.BTN_3
        ], name='Mazda 3')


    def read_can( self, msg_id, msg_b ):
        if msg_id == 0x4da: 
            pass    
        elif msg_id == 0x201:
            pass
        elif msg_id == 0x190:
            pass
        elif msg_id == 0x4ec:
            pass
        elif msg_id == 0x433:
            pass
        

if __name__ == '__main__':
    args = {}
    if len( sys.argv ) < 2:
        print('Usage: {} filter [device] [baud_rate] [protocol]')
        sys.exit(1)
    filter = int( sys.argv[1] ) 
    assert 0 <= filter <= 7

    if len( sys.argv ) >= 3:
        args['device'] = sys.argv[2]
    if len( sys.argv ) >= 4:
        args['baud_rate'] = sys.argv[3]
    if len( sys.argv ) >= 5:
        args['protocol'] = sys.argv[4]

    elm = ELM327( **args )
    elm.reset()

    last_msg = {}

    
    try:
        while True:
            msg_id, msg_b = elm.
            msg_m = msg_re.match(msg_raw)
            if msg_m:
                msg_id = int(msg_m.group(1), 16)
                msg_b = bytes(map(lambda x: int(x, 16), msg_m.group(2).strip().split(b' ')))
                if msg_id not in last_msg:
                    last_msg[msg_id] = msg_b
                elif last_msg[msg_id][:-1] != msg_b[:-1]:
                    print('{0:#03x}: {1} -> {2}'.format(msg_id, last_msg[msg_id], msg_b))
                    last_msg[msg_id] = msg_b
            else:
                print('-- Miss: {}'.format(msg_raw))
    except EOFError:
        print('-- Hit the end')
    except KeyboardInterrupt:
        pass
