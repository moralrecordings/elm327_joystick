#!/usr/bin/env python3

import sys
import math

import uinput
from elm327 import ELM327
from mrcrowbar import models as mrc


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
    def __init__( self, name, mapping ):
        # create a new virtual joystick device with the features we need 
        self.device = uinput.Device( mapping, name )
        self.steering = 0
        self.accelerator = 0
        self.brake = 0
        self.high_beams = 0
        self.cruise = 0
        self.driver_door = 0


    def update( self, msg_id, msg_b ):
        cruise_old = self.cruise
        driver_door_old = self.driver_door

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
        super( Mazda3Joystick, self ).__init__( name=self.NAME, mapping=self.DEVICE )

    def set_controls( self ): 
        self.device.emit( uinput.ABS_WHEEL, self.steering )
        self.device.emit( uinput.ABS_GAS, self.accelerator )
        self.device.emit( uinput.BTN_0, self.brake )
        self.device.emit( uinput.BTN_1, self.high_beams )
        self.device.emit( uinput.BTN_2, 1 if self.cruise != cruise_old else 0 )
        self.device.emit( uinput.BTN_3, 1 if self.driver_door != driver_door_old else 0 )
        return
        

class Mazda3Keyboard( Mazda3 ):
    
    NAME = 'Mazda 3 Keyboard'
    DEVICE = [
        uinput.KEY_LEFT,
        uinput.KEY_UP,
        uinput.KEY_RIGHT,
        uinput.KEY_DOWN,
        uinput.KEY_LEFTSHIFT,
        uinput.KEY_SPACE,
        uinput.KEY_LEFTCTRL,
        uinput.KEY_ENTER
    ]
    PRESS_THRESHOLD = 32
    SHOVE_THRESHOLD = 96
    

    def __init__( self ):
        super( Mazda3Keyboard, self ).__init__( name=self.NAME, mapping=self.DEVICE )

    def set_controls( self ): 
        self.device.emit( uinput.KEY_LEFT, 1 if self.steering < -self.PRESS_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_RIGHT, 1 if self.steering > self.PRESS_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_UP, 1 if self.accelerator > self.PRESS_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_LEFTSHIFT, 1 if self.accelerator > self.SHOVE_THRESHOLD else 0 )
        self.device.emit( uinput.KEY_DOWN, self.brake )
        self.device.emit( uinput.KEY_LEFTCTRL, self.high_beams )
        self.device.emit( uinput.KEY_SPACE, 1 if self.cruise != cruise_old else 0 )
        self.device.emit( uinput.KEY_ENTER, 1 if self.driver_door != driver_door_old else 0 )
        return



if __name__ == '__main__':
    args = {}
    controller = None
    if len( sys.argv ) >= 2 and sys.argv[1] == 'keyboard':
        controller = Mazda3Keyboard()
    else:
        controller = Mazda3Joystick()
    if len( sys.argv ) >= 3:
        args['device'] = sys.argv[2]
    if len( sys.argv ) >= 4:
        args['baud_rate'] = sys.argv[3]
    if len( sys.argv ) >= 5:
        args['protocol'] = sys.argv[4]

    controller = Mazda3Joystick()

    elm = ELM327( **args )
    elm.reset()
    elm.set_can_whitelist( [0x4da, 0x201, 0x205, 0x4ec, 0x433] )
    elm.start_can()
    
    try:
        while True:
            msg_id, msg_b = elm.recv_can()
            if msg_b:
                controller.update( msg_id, msg_b )
            else:
                print('-- Miss: {}'.format(msg_raw))
    except EOFError:
        print('-- Hit the end')
    except KeyboardInterrupt:
        pass
    elm.get_prompt()
