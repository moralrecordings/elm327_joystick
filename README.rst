ELM327 Joystick
###############

This repository contains scripts useful for wiring the controls of a car (e.g. steering, accelerator and brakes) to a virtual keyboard/game controller. The project was documented in the writeup `"Using your car as a giant joystick for $20" <https://moral.net.au>`_.

In these scripts, input from the car is achieved by using a cheap ELM327 OBD-II adapter to monitor the CANbus, and output is handled via the Linux uinput driver. Included is a generic communications harness for the ELM327, a simple scanning program that monitors for changes on the CANbus, and some example joysticks for the 2007 Mazda 3.

Usage
=====

To run this, you can `create a virtualenv for Python 3 <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_ and run the scripts:

.. code:: bash

    cd elm327_joystick
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    ./elm_scan.py --help

elm_scan.py is a tool useful for determining which controls in the car produce CANbus output. As mentioned in the writeup, every car model has a different proprietary CANbus message format. In general CANbus messages have an ID that denotes the message type, and a 2-10 byte body with multiple sensor readings packed in. ECUs in the car will constantly send out messages multiple times a second, even if there are no changes to the sensors; to counteract this elm_scan.py will only print out messages with changed content.

You can run elm_scan.py to map out the controls of your car, then use the layout of mazda3_joystick.py as an example for building your own car-to-joystick layer. I recommend having a common base class that interprets CANbus messages and keeps track of the car input state, and a child class for each (game-specific) mapping of state to keyboard/joystick events.

Licensing
=========

ELM327 Joystick is licensed under the BSD 3-Clause license. Go nuts.
