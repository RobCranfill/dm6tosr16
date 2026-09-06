# dm6tosr16
MIDI router for drum kit to drum synth.

A Linux version of what I wish I could do on a CircuitPython microprocessor.

My DM6 e-drum kit has a lame set of sounds built in. I wanted to use the nicer sounds
in my SR16 (or SR18) Roland drum synth - but the DM6 uses USB MIDI, whereas the SR16/18
are old-school DIN5 MIDI connectors.

This app, running on a Raspbery Pi Zero 2W ("2W" aspect not required) with an old
USB MIDI interface (a MIDISport Uno - ancient!) works just fine.

The most complicated thing is the GUI that lets you shut the system down nicely,
since it's a Linux box and doesn't like having its power pulled while running.


# Concept of Operation
## MIDI Routing
Is handled by a couple calls to the standard Linux ALSA MIDI command 'aconnect'.

## GUI
Shows status - what? - and allows nice shutdown.

## Scripts
A bunch of Linux stuff so the system runs automagically.


# Requirements
 * Raspberry Pi Zero of some sort, running RPi OS (I used Debian 13/"Trixie").
 * DIN5 MIDI interface that Linux recognizes.
 * Adafruit "Blinka" library
   * Had to jump thru hoops for ''
 * This project.

# Running

# Thoughts

# To Do
## Python
  * Handle interrupts
    * ^C: turn off backlight
    * SIGINT? or something for 'going down'?
## Scripts
  * Can service keep the app alive? I think so.
