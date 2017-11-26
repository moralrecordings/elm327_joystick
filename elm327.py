
import serial
import sys
import time
import re

CAN_RE = re.compile( b'([0-9A-F]{3})\\W*([0-9A-F\\W]+)' )

# Protocol mapping (taken from ELM327 datasheet)
# '0': Autodetect (everything except User1 and User2)
# '1': SAE J1850 PWM (41.6 kbaud)
# '2': SAE J1850 VPW (10.4 kbaud)
# '3': ISO 9141-2 (5 baud init)
# '4': ISO 14230-4 KWP (5 baud init)
# '5': ISO 14230-4 KWP (fast init)
# '6': ISO 15765-4 CAN (11 bit ID, 500 kbaud)
# '7': ISO 15765-4 CAN (29 bit ID, 500 kbaud)
# '8': ISO 15765-4 CAN (11 bit ID, 250 kbaud)
# '9': ISO 15765-4 CAN (29 bit ID, 250 kbaud)
# 'A': SAE J1939 CAN (29 bit ID, 250* kbaud)
# 'B': User1 CAN (11* bit ID, 125* kbaud)
# 'C': User2 CAN (11* bit ID, 50* kbaud)

class ELM327:
    
    def __init__( self, device='/dev/ttyUSB0', baud_rate='500000', protocol='0' ):
        self.elm = serial.Serial( device, baud_rate )
        self.protocol = protocol


    def send( self, cmd ):
        self.elm.reset_input_buffer()
        self.elm.reset_output_buffer()
        self.elm.write( cmd )
        self.elm.write( b'\r' )
    

    def recv( self ):
        output = bytearray()
        while True:
            b = self.elm.read( 1 )
            if b == b'>':
                break
            output.append( b[0] )
        print( output )
        return output


    def recv_line( self ):
        output = bytearray()
        while True:
            b = self.elm.read( 1 )
            if b == b'\r':
                break
            elif b == b'>':
                raise EOFError
            output.append( b[0] )
        #print( output )
        return output


    def recv_can( self ):
        msg_raw = self.recv_line()
        msg_m = CAN_RE.match( msg_raw )
        #print( msg_raw )
        if msg_m:
            msg_id = int( msg_m.group( 1 ), 16 )
            msg_b = bytes.fromhex( msg_m.group( 2 ).decode( 'ascii' ) )
            return (msg_id, msg_b)
        if msg_raw.startswith( b'SEARCHING' ):
            raise EOFError
        return (-1, msg_raw)


    def get_prompt( self ):
        self.send( b'this will reset the prompt' )
        self.recv()


    def reset( self ):
        # reset interface
        self.get_prompt()
        self.send( b'AT Z' )
        self.recv()

        # return to defaults
        self.send( b'AT D' )
        self.recv()

        # turn echo off
        self.send( b'AT E0' )
        self.recv()

        # check that information string works
        self.send( b'AT I' )
        ack = self.recv()
        print( ack )
        assert ack.startswith( b'ELM' )

        # set the CANbus protocol used by the car
        self.send( 'AT SP {}'.format( self.protocol ).encode('ascii') )
        self.recv()

        # initialize the CANbus interface
        self.send( b'0100' )
        print( self.recv() )

        # get protocol 
        self.send( b'AT DPN' )
        print( self.recv() )

        # enable messages longer than 7 bytes (standards are for chumps!)
        self.send( b'AT AL' )
        self.recv()

        # turn on headers
        self.send( b'AT H1' )
        self.recv()

        # disable formatting
        self.send( b'AT CAF0' )
        self.recv()

        # disable extra whitespace (~30% extra buffer space!)
        self.send( b'AT S0' )
        self.recv()

        # set huuuuge timeout
        self.send( b'AT STFF' )
        self.recv()

        print( '-- device ready' )


    def start_can( self ):
        self.get_prompt()
        self.send( b'AT MA' )


    def set_can_filter( self, filter ):
        self.get_prompt()
        self.send( 'AT CF {0:03x}'.format( filter ).encode( 'ascii' ) )
        self.recv()
        

    def set_can_mask( self, mask ):
        self.get_prompt()
        self.send( 'AT CM {0:03x}'.format( mask ).encode( 'ascii' ) )
        self.recv()
    

    def set_can_and( self, mask ):
        cf = mask
        cm = 0x7ff ^ mask
        self.set_can_filter( cf )
        self.set_can_mask( cm )


    def set_can_whitelist( self, message_ids=None ):
        cf = 0
        cm = 0
        if message_ids:
            # generage a CAN ID filter/mask
            # we are matching bits that *don't change* for all 11-bit message IDs?
            cf = message_ids[0]
            cm = 0x7ff
            for m in message_ids[1:]:
                cm &= ((cf ^ m) ^ 0x7ff)

        self.set_can_filter( cf )
        self.set_can_mask( cm )
        

