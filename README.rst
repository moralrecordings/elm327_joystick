ELM327 Joystick
###############

This repository contains scripts to assist in connecting up the controls of a car (e.g. steering, accelerator and brakes) to a Linux virtual keyboard/game controller, by intercepting CANbus messages with a cheap ELM327 OBD-II adapter. The project was documented in the writeup `"Using your car as a giant joystick for $20" <https://moral.net.au>`_.

Included is the generic communications harness for the ELM327, and some example joysticks for the 2007 Mazda 3.

Usage
=====

To run this, you can `create a virtualenv for Python 3 <http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/>`_ and run the scripts:

.. code:: bash

    cd elm327_joystick
    virtualenv -p /usr/bin/python3 venv
    source venv/bin/activate
    pip install -r requirements.txt
    ./elm_scan.py --help

elm_scan.py is a tool useful for determining which controls in the car produce useful CANbus output. As mentioned in the writeup, every car model has a different proprietary CANbus message format. ECUs in the car pack multiple sensors into a message with a unique type ID, then repeatedly send these messages on the CANbus. By default elm_scan.py will print out only the messages that have changed, which cuts out most of the irrelevant traffic.

The game control configurations I made for the demo are stored in mazda3_joystick.py, but they will not work with anything other than a 2007 Mazda 3. You can run elm_scan.py to map out the controls of your car, then use the layout of mazda3_joystick.py as an example for building your own car-to-joystick layer. I recommend having a common base class that interprets CANbus messages and keeps track of the car input state, and a child class for each (game-specific) mapping of state to keyboard/joystick events.

Licensing
=========

ELM327 Joystick is licensed under the BSD 3-Clause license. Go nuts.
