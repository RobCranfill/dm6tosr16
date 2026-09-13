#!/bin/bash

# Connect DM6 and MidiSport
# Based on a script by Antonio Bonifati.
# from http://www.tedfelix.com/linux/linux-midi.html

logger $0 running at `date`

# Use aconnect to get the ports
dm6port=$(aconnect    --input  | grep -i "e-drum"          | head -1 | cut -d ' ' -f 2)0
midisport=$(aconnect  --output | grep -i "MidiSport 1x1"   | head -1 | cut -d ' ' -f 2)0
pythonport=$(aconnect --output | grep -i "RtMidiIn Client" | head -1 | cut -d ' ' -f 2)0

echo dm6 input port: $dm6port
echo midi output port: $midisport
echo python port: $pythonport

# Connect the ports
aconnect --removeall
aconnect $dm6port $midisport
aconnect $dm6port $pythonport
