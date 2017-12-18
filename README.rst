ELM327 Joystick
###############

This repository contains scripts useful for wiring the controls of a car (e.g. steering, accelerator and brakes) to a virtual keyboard/game controller. 

The project was documented in the writeup `"Using your car as a giant joystick for $20" <https://moral.net.au/writing/2017/12/18/canbus_car_game_controller/>`_. Input from the car is scraped with a cheap ELM327 OBD-II adapter monitoring the CANbus, and output is handled via the Linux uinput driver. Included is a small communications harness for the ELM327, a simple scanning program that monitors for changes on the CANbus, and some example joysticks for the 2007 Mazda 3 used in the demo.

Usage
=====

To run these, `create a virtualenv for Python 3 <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_ first:

.. code:: bash
    
    cd elm327_joystick
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate

Before using the scripts I would suggest using a serial terminal to set your ELM327 to the highest possible baud rate. The chip only has 256 bytes to buffer CAN mesages **as ASCII**, so the faster the better. The communications harness in elm327.py will make the messages as compact as possible, but the baud rate is device specific and needs to be manually set. In the writeup I walk through the process in the section "Changing the comms speed"; here's the TL;DR for someone changing an ELM327 running at the stock rate of 38400 baud to the counterfeit-ELM327-ceiling of 500000 baud. (Remember if you have any other software that uses the ELM327, it will not work until you bring back the stock baud rate with the command "AT PP 0C OFF").

.. code:: bash

    cd elm327_joystick
    source venv/bin/activate
    pip install ssterm
    ssterm /dev/ttyUSB0 -b 38400 --rx-nl cr --tx-nl cr
    
    ?

    >AT PP 0C SV 08
    OK

    >AT PP 0C ON
    OK

    >AT Z
    ...
    ssterm /dev/ttyUSB0 -b 500000 --rx-nl cr --tx-nl cr

    ?

    >AT I
    ELM327 v1.4

elm_scan.py is a tool useful for determining which controls in the car produce CANbus output; basically a cheapo equivalent of "cansniffer" from the Linux CAN utils. In general every car model has a different proprietary CANbus message format; messages have an ID that denotes the message type, and a 2-10 byte body with multiple sensor readings packed in. ECUs in the car will constantly send out messages multiple times a second, even if there are no changes to the message body; to counteract this elm_scan.py will only print out messages with changed content.

.. code:: bash

    cd elm327_joystick
    source venv/bin/activate
    pip install -r requirements.txt
    ./elm_scan.py --help

You can run elm_scan.py to map out the controls of your car, then use the layout of mazda3_joystick.py as an example for building your own car-to-joystick layers. I recommend having a common base class that interprets CANbus messages and keeps track of the car input state, and a child class for each (game-specific) mapping of state to keyboard/joystick events.

Licensing
=========

ELM327 Joystick is licensed under the BSD 3-Clause license. Go nuts.
