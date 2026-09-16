#!/bin/bash
# script to run piflight at startup

cd /home/rob/proj/dm6tosr16

# Route the MIDI signals....
./connect_dm6tosr16.sh

# ... and run the Python GUI.

. env/bin/activate
python3 dm6tosr16_gui_pil.py
