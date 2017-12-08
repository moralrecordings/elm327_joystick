#!/usr/bin/env python3

import uinput
from elm327 import ELM327, PROTOCOLS
from mrcrowbar import models as mrc

import math
import time
from optparse import OptionParser

class OptParser( OptionParser ):
    def format_epilog( self, formatter ):
        return '\n{}\n'.format( '\n'.join( [formatter._format_text( x ) for x in self.epilog.split( '\n' )] ) )


class Steering( mrc.Block ):
    RANGE = 0x00D2

    axis_raw = mrc.UInt16_BE( 0x00 )

    @property
    def axis( self ):
        return min( max( (255*(self.axis_raw - 0x8000)//self.RANGE), -255 ), 255 )


class Accelerator( mrc.Block ):
    RANGE = 0xC8

    axis_raw = mrc.UInt8( 0x06 )

    @property
    def axis( self ):
        return min( max( (255*(self.axis_raw)//self.RANGE), 0 ), 255 )


class Brake( mrc.Block ):
    button = mrc.Bits( 0x02, 0b01000000 )


class Cruise( mrc.Block ):
    button = mrc.Bits( 0x00, 0b10000000 )


class Controls( mrc.Block ):
    driver_door = mrc.Bits( 0x00, 0b10000000 )
    high_beams = mrc.Bits( 0x03, 0b01000000 )


class Mazda3:
    LATCH_TIME = 0.1
    PRESS_THRESHOLD = 32
    STEER_THRESHOLD = 64
    SHOVE_THRESHOLD = 128

    def __init__( self, name, mapping ):
        print( 'Creating uinput device "{}"...'.format( name ) )
        self.device = uinput.Device( mapping, name )
        self.steering = 0
        self.accelerator = 0
        self.brake = 0
        self.high_beams = 0
        self.cruise_t = self.driver_door_t = time.time() + self.LATCH_TIME
        self.cruise = 0
        self.driver_door = 0
        self.cruise_prev = 0
        self.driver_door_prev = 0

    def update( self, msg_id, msg_b ):
        t = time.time()
        self.cruise_prev = self.cruise
        self.driver_door_prev = self.driver_door

        if msg_id == 0x4da:
            self.steering = Steering( msg_b ).axis
        elif msg_id == 0x201:
            self.accelerator = Accelerator( msg_b ).axis
        elif msg_id == 0x205:
            self.brake = Brake( msg_b ).button
        elif msg_id == 0x4ec:
            self.cruise = Cruise( msg_b ).button
        elif msg_id == 0x433:
            obj = Controls( msg_b )
            self.high_beams = obj.high_beams
            self.driver_door = obj.driver_door
        else:
            return
        
        if self.cruise != self.cruise_prev:
            self.cruise_t = t
        if self.driver_door != self.driver_door_prev:
            self.driver_door_t = t

        self.set_controls()
        return
        
    
    def set_controls( self ):
        pass


class Mazda3Joystick( Mazda3 ):
    
    NAME = 'Mazda 3 Joystick'
    DEVICE = [
        uinput.ABS_WHEEL + (-255, 255, 0, 0),
        uinput.ABS_GAS + (0, 255, 0, 0),
        uinput.BTN_0,
        uinput.BTN_1,
        uinput.BTN_2,
        uinput.BTN_3
    ]

    def __init__( self ):
        super().__init__( name=self.NAME, mapping=self.DEVICE )

    def set_controls( self ): 
        t = time.time()
        self.device.emit( uinput.ABS_WHEEL, self.steering )
        self.device.emit( uinput.ABS_GAS, self.accelerator )
        self.device.emit( uinput.BTN_0, self.brake )
        self.device.emit( uinput.BTN_1, self.high_beams )
        self.device.emit( uinput.BTN_2, 1 if t < (self.cruise_t + self.LATCH_TIME) else 0 )
        self.device.emit( uinput.BTN_3, 1 if t < (self.driver_door_t + self.LATCH_TIME) else 0 )
        return


class Mazda3Doom( Mazda3Joystick ):
    
    NAME = 'Mazda 3 Doom'
    DEVICE = [
        uinput.ABS_WHEEL + (-255, 255, 0, 0),
        uinput.ABS_GAS + (-255, 255, 0, 0),
        uinput.BTN_0,
        uinput.BTN_1,
        uinput.BTN_2,
        uinput.BTN_3
    ]


class Mazda3DOS( Mazda3Joystick ):
    
    NAME = 'Mazda 3 DOS'
    DEVICE = [
        uinput.ABS_WHEEL + (-255, 255, 0, 0),
        uinput.ABS_GAS + (-255, 255, 0, 0),
        uinput.BTN_0,
        uinput.BTN_1,
        uinput.BTN_2,
        uinput.BTN_3
    ]

    def set_controls( self ): 
        t = time.time()
        self.device.emit( uinput.ABS_WHEEL, self.steering )
        self.device.emit( uinput.ABS_GAS, self.accelerator*2-255 )
        self.device.emit( uinput.BTN_0, self.brake )
        self.device.emit( uinput.BTN_1, self.high_beams )
        self.device.emit( uinput.BTN_2, 1 if t < (self.cruise_t + self.LATCH_TIME) else 0 )
        self.device.emit( uinput.BTN_3, 1 if t < (self.driver_door_t + self.LATCH_TIME) else 0 )
        return


class Mazda3Descent( Mazda3 ):
    
    NAME = 'Mazda 3 Descent'
    DEVICE = [
        uinput.ABS_WHEEL + (-255, 255, 0, 0),
        uinput.ABS_GAS + (-255, 255, 0, 0),
        uinput.BTN_0,
        uinput.BTN_1,
        uinput.BTN_2,
        uinput.BTN_3,
        uinput.KEY_UP,
        uinput.KEY_DOWN
    ]

    DOUBLE_TAP = 0.5

    def __init__( self ):
        super().__init__( name=self.NAME, mapping=self.DEVICE )
        self.high_beams_prev = 0
        self.high_beams_t = time.time()
        self.high_beams_key = uinput.KEY_DOWN

    def update( self, msg_id, msg_b ):
        t = time.time()
        self.high_beams_prev = self.high_beams
        super().update( msg_id, msg_b )

        if self.high_beams != self.high_beams_prev:
            if self.high_beams:
                self.high_beams_key = uinput.KEY_UP if (t - self.high_beams_t < self.DOUBLE_TAP) else uinput.KEY_DOWN
                self.device.emit( self.high_beams_key, 1 )
                self.high_beams_t = t
            else:
                self.device.emit( self.high_beams_key, 0 )


    def set_controls( self ): 
        t = time.time()
        
        self.device.emit( uinput.ABS_WHEEL, self.steering )
        self.device.emit( uinput.ABS_GAS, self.accelerator )

        self.device.emit( uinput.BTN_0, self.brake )
        self.device.emit( uinput.BTN_2, 1 if t < (self.cruise_t + self.LATCH_TIME) else 0 )
        self.device.emit( uinput.BTN_3, 1 if t < (self.driver_door_t + self.LATCH_TIME) else 0 )
        return
        

class Mazda3Grim( Mazda3 ):
    
    NAME = 'Mazda 3 Grim Fandango'
    DEVICE = [
        uinput.KEY_LEFT,
        uinput.KEY_UP,
        uinput.KEY_RIGHT,
        uinput.KEY_U,
        uinput.KEY_LEFTSHIFT,
        uinput.KEY_E,
        uinput.KEY_P,
        uinput.KEY_I
    ]
    

    def __init__( self ):
        super().__init__( name=self.NAME, mapping=self.DEVICE )

    def set_controls( self ): 
        t = time.time()
        self.device.emit( uinput.KEY_LEFT, 1 if self.steering < -self.STEER_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_RIGHT, 1 if self.steering > self.STEER_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_UP, 1 if self.accelerator > self.PRESS_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_LEFTSHIFT, 1 if self.accelerator > self.SHOVE_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_U, self.brake )
        self.device.emit( uinput.KEY_E, self.high_beams )
        self.device.emit( uinput.KEY_P, 1 if t < self.cruise_t + self.LATCH_TIME else 0 )
        self.device.emit( uinput.KEY_I, 1 if t < self.driver_door_t + self.LATCH_TIME else 0 )
        return


class Mazda3Sonic( Mazda3 ):
    
    NAME = 'Mazda 3 Sonic'
    DEVICE = [
        uinput.KEY_LEFT,
        uinput.KEY_UP,
        uinput.KEY_RIGHT,
        uinput.KEY_DOWN,
        uinput.KEY_Z,
        uinput.KEY_ENTER
    ]
    

    def __init__( self ):
        super().__init__( name=self.NAME, mapping=self.DEVICE )

    def set_controls( self ): 
        t = time.time()
        self.device.emit( uinput.KEY_LEFT, 1 if self.steering < -self.STEER_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_RIGHT, 1 if self.steering > self.STEER_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_Z, 1 if self.accelerator > self.PRESS_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_DOWN, self.brake )
        self.device.emit( uinput.KEY_UP, self.high_beams )
        self.device.emit( uinput.KEY_ENTER, 1 if t < self.cruise_t + self.LATCH_TIME else 0 )
        return



CONTROLLERS = {
    'joystick': Mazda3Joystick,
    'grim': Mazda3Grim,
    'descent': Mazda3Descent,
    'doom': Mazda3Doom,
    'dos': Mazda3DOS,
    'sonic': Mazda3Sonic,
}


if __name__ == '__main__':
    usage = 'Usage: %prog [options]'
    parser = OptParser( epilog='Protocols supported by the ELM327:\n{}'.format( PROTOCOLS ) )
    parser.add_option( '-g', '--game', dest='game', help='Game configuration to use (choices: {})'.format( ' '.join( CONTROLLERS.keys() ) ) )
    parser.add_option( '-d', '--device', dest='device', help='Path to ELM327 serial device' )
    parser.add_option( '-b', '--baudrate', dest='baud_rate', help='Baud rate' )
    parser.add_option( '-p', '--protocol', dest='protocol', help='ELM327 message protocol to use' )

    (options, argv) = parser.parse_args()

    args = {}
    controller_type = 'joystick'
    if options.game and options.game in CONTROLLERS:
        controller_type = options.game
    elif len( argv ) >= 1 and argv[0] in CONTROLLERS:
        controller_type = argv[0]
    controller = CONTROLLERS[controller_type]()

    if options.device:
        args['device'] = options.device
    elif len( argv ) >= 2:
        args['device'] = argv[1]
    if options.baud_rate:
        args['baud_rate'] = options.baud_rate
    elif len( argv ) >= 3:
        args['baud_rate'] = argv[2]
    if options.protocol:
        args['protocol'] = options.protocol
    elif len( argv ) >= 4:
        args['protocol'] = argv[3]

    elm = ELM327( **args )
    elm.reset()
    elm.set_can_whitelist( [0x4da, 0x201, 0x205, 0x4ec, 0x433] )
    elm.start_can()
    
    try:
        while True:
            msg_id, msg_b = elm.recv_can()
            if msg_id >= 0:
                controller.update( msg_id, msg_b )
            else:
                print('-- Miss: {}'.format( msg_b ))
    except EOFError:
        print('-- Hit the end')
    except KeyboardInterrupt:
        pass
    elm.get_prompt()
