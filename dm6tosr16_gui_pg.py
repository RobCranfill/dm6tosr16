"""
dm6tosr16 gui
 adapted from
    https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-stats
"""

import os
import signal
import subprocess
import sys
import time

import board
import digitalio

# MIDO Python/MIDI lib
import mido

# Use PyGame for GUI?
import mini_pi_tft_display


print(f"{sys.argv[0]} starting up...")

# Count down from this for reboot:
REBOOT_COUNT = 5

BACKLIGHT_PIN = board.D22
_backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
_backlight.switch_to_output()

def backlight_off():
    _backlight.value = False

_keep_running = True

# SIGTERM is sent to a service on system shutdown. Handle it.
# We want to turn off the _backlight at least.
def signal_handler(sig, frame):
    print(f"Signal {sig} caught; terminating.")
    # backlight_off()
    _keep_running = False

signal.signal(signal.SIGTERM, signal_handler)


# PyGame!

_display = mini_pi_tft_display.tft_display()


# Turn on the _backlight
_backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
_backlight.switch_to_output()
_backlight.value = True


button24 = digitalio.DigitalInOut(board.D24)
button24.direction = digitalio.Direction.INPUT
button24.pull = digitalio.Pull.UP


# Find the right input port to connect to
print("Opening ALSA MIDI input port...")

use_port = None
while use_port is None:
    ports = mido.get_input_names()
    for port_name in ports:
        if "DM6" in port_name:
            use_port = port_name
        elif "MPK" in port_name:
            use_port = port_name

print(f"Using MIDI port {use_port}")
midi_port = mido.open_input(use_port)


# For reboot function. Count down from this max.
count = REBOOT_COUNT
button_was_pushed = False


# TODO: this doesn't really work??
def blank_screen(draw):

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)



# Status message at bottom of screen
extra_msg = ""

start_time = time.monotonic()
midi_event_count = 0

# Main event loop. Catch exceptions and either restart and keep going, or die.
#
while _keep_running :

    try:

        # We just want to count the messages.
        for msg in midi_port.iter_pending():
            midi_event_count += 1

        extra_msg = None

        # Shutdown button pushed?
        #
        button_is_pushed = not button24.value
        if button_is_pushed:
            if not button_was_pushed:
                extra_msg = f"Shutdown in {REBOOT_COUNT}..."
                print(extra_msg)
            else:
                count -= 1
                extra_msg = f"Shutdown in {count}..."
                print(extra_msg)
                if count == 0:
                    print(f"{sys.argv[0]} shutting down!")
                    # Won't work if run in user space, but OK as service. Fine.
                    os.system("shutdown -h now")
                    time.sleep(60) # TODO: needed? useful?
            button_was_pushed = True
        else:
            if button_was_pushed:
                extra_msg = "Shutdown aborted."
                print(extra_msg)
                button_was_pushed = False
                count = REBOOT_COUNT

        if extra_msg is None:
            uptime = int(time.monotonic() - start_time)
            extra_msg = f"Up {uptime} seconds"


        _display.update(123, 456, "Just testing")

        # _display.update(extra_msg, midi_event_count)

        time.sleep(0.2)

    # TODO: Does ^C get caught here, or does the signal handler get it?
    except KeyboardInterrupt:
        print("\n^C caught; terminating.")
        # backlight_off()
        _keep_running = False

# Done!
blank_screen(draw_object)
backlight_off()
print(f"{sys.argv[0]} dropping out of main event loop.")
