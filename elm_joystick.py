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
    driver_door =   mrc.Bits( 0x00, 0b10000000 )
    high_beams =    mrc.Bits( 0x03, 0b01000000 )


class Mazda3:
    def __init__( self ):
        # create a new virtual joystick device with the features we need 
        self.device = uinput.Device([
            uinput.ABS_WHEEL + (-255, 255, 0, 0),
            uinput.ABS_GAS + (0, 255, 0, 0),
            uinput.BTN_0,
            uinput.BTN_1,
            uinput.BTN_2,
            uinput.BTN_3
        ], name='Mazda 3')
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
            self.high_beams = Controls( msg_b ).high_beams
            self.driver_door = Controls( msg_b ).driver_door
        else:
            return
    
        self.device.emit( uinput.ABS_WHEEL, self.steering )
        self.device.emit( uinput.ABS_GAS, self.accelerator )
        self.device.emit( uinput.BTN_0, self.brake )
        self.device.emit( uinput.BTN_1, self.high_beams )
        self.device.emit( uinput.BTN_2, 1 if self.cruise != cruise_old else 0 )
        self.device.emit( uinput.BTN_3, 1 if self.driver_door != driver_door_old else 0 )
        

if __name__ == '__main__':
    args = {}

    if len( sys.argv ) >= 2:
        args['device'] = sys.argv[1]
    if len( sys.argv ) >= 3:
        args['baud_rate'] = sys.argv[2]
    if len( sys.argv ) >= 4:
        args['protocol'] = sys.argv[3]

    joystick = Mazda3()

    elm = ELM327( **args )
    elm.reset()
    elm.set_can_whitelist( [0x4da, 0x201, 0x205, 0x4ec, 0x433] )
    elm.start_can()
    
    try:
        while True:
            msg_id, msg_b = elm.recv_can()
            #print((msg_id, msg_b))
            if msg_b:
                joystick.update( msg_id, msg_b )
    except EOFError:
        print('-- Hit the end')
    except KeyboardInterrupt:
        elm.get_prompt()
        pass
