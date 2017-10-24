#!/usr/bin/env python3 
import sys

from elm327 import ELM327

SUBSETS = {
    0x20f: (0, 7),
    0x211: (0, 7),
}


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
    elm.set_can_filter( 0x7ff )
    elm.set_can_mask( filter << 8 )
    elm.start_can()

    last_msg = {}

    try:
        while True:
            msg_id, msg_b = elm.recv_can()
            if msg_b:
                if msg_id in SUBSETS:
                    msg_b = msg_b[SUBSETS[msg_id][0]:SUBSETS[msg_id][1]]
                if msg_id not in last_msg:
                    last_msg[msg_id] = msg_b
                elif last_msg[msg_id] != msg_b:
                    print( '{0:03x}: {1} -> {2}'.format(msg_id, last_msg[msg_id], msg_b.hex()) )
                    last_msg[msg_id] = msg_b
    except EOFError:
        print('-- Hit the end')
    except KeyboardInterrupt:
        pass
    elm.get_prompt()
