#!/usr/bin/env python3 
from elm327 import ELM327, PROTOCOLS

from optparse import OptionParser

class OptParser( OptionParser ):
    def format_epilog( self, formatter ):
        return '\n{}\n'.format( '\n'.join( [formatter._format_text( x ) for x in self.epilog.split( '\n' )] ) )


# define your own ignore message byteranges in here 
#SUBSETS = {
#    0x20f: (0, 7),
#    0x211: (0, 7),
#}

if __name__ == '__main__':
    usage = 'Usage: %prog [options]'
    parser = OptParser( epilog='Protocols supported by the ELM327:\n{}'.format( PROTOCOLS ) )
    parser.add_option( '-d', '--device', dest='device', help='Path to ELM327 serial device' )
    parser.add_option( '-b', '--baudrate', dest='baud_rate', help='Baud rate' )
    parser.add_option( '-p', '--protocol', dest='protocol', help='ELM327 message protocol to use' )
    parser.add_option( '-f', '--full', action='store_true', default=False, dest='full', help='Show all incoming CAN messages, instead of just changes to messages' )
    parser.add_option( '-i', '--ignore', dest='ignore', help='Comma seperated list of message IDs to ignore' )
    parser.add_option( '-c', '--can-filter', dest='can_filter', help='Set message ID filter' )
    parser.add_option( '-m', '--can-mask', dest='can_mask', help='Set message ID mask' )

    (options, argv) = parser.parse_args()

    args = {}
    if options.device:
        args['device'] = options.device
    elif len( argv ) >= 1:
        args['device'] = argv[0]
    if options.baud_rate:
        args['baud_rate'] = options.baud_rate
    elif len( argv ) >= 2:
        args['baud_rate'] = argv[1]
    if options.protocol:
        args['protocol'] = options.protocol
    elif len( argv ) >= 3:
        args['protocol'] = argv[2]

    elm = ELM327( **args )
    elm.reset()

    if options.can_filter:
        elm.set_can_filter( int( options.can_filter, 0 ) )
    if options.can_mask:
        elm.set_can_mask( int( options.can_mask, 0 ) )
    IGNORE = []
    if options.ignore:
        IGNORE = [int( x.strip(), 0 ) for x in options.ignore.split(',')]

    elm.start_can()

    firehose = options.full

    last_msg = {}

    try:
        while True:
            msg_id, msg_b = elm.recv_can()
            if msg_b:
                #if msg_id in SUBSETS:
                #    msg_b = msg_b[SUBSETS[msg_id][0]:SUBSETS[msg_id][1]]
                if msg_id in IGNORE:
                    pass
                if msg_id not in last_msg:
                    last_msg[msg_id] = msg_b
                elif firehose or (last_msg[msg_id] != msg_b):
                    print( '{0:03x}: {1} -> {2}'.format( msg_id, last_msg[msg_id].hex(), msg_b.hex() ) )
                    last_msg[msg_id] = msg_b
    except EOFError:
        print( '-- Hit the end' )
    except KeyboardInterrupt:
        pass
    elm.get_prompt()
