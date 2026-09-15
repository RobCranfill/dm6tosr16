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
from adafruit_rgb_display import st7789

# MIDO Python/MIDI lib
import mido

# Python Image Library
from PIL import Image, ImageDraw, ImageFont


# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# FONT_PATH = "fonts/upheaval.ttf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

print(f"{sys.argv[0]} starting up...")


# Count down from this for reboot:
REBOOT_COUNT = 5

# Configuration for Adafruit 1.3" 240x240 TFT
CS_PIN = digitalio.DigitalInOut(board.CE0)
DC_PIN = digitalio.DigitalInOut(board.D25)
RESET_PIN =  None
HEIGHT = 240
WIDTH = 240
BAUDRATE = 64000000

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


# Init the ST7789 display.
disp = st7789.ST7789(
    board.SPI(),
    cs=CS_PIN,
    dc=DC_PIN,
    rst=RESET_PIN,
    baudrate=BAUDRATE,
    width=WIDTH,
    height=HEIGHT,
    x_offset=0,
    y_offset=80 # magic number?
    )

# Create a blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
image = Image.new("RGB", (WIDTH, HEIGHT))
rotation = 180 # buttons on the left - USB connectors down on RPi.

# Get drawing object to draw on image.
draw_object = ImageDraw.Draw(image)

# Display constants
display_left = 0
top = -2

# Load a TrueType font.
_font = ImageFont.truetype(FONT_PATH, 24)

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


def update_display(draw, status_message, midi_count):

    # TODO: is this the best way to display this? Can I use labels instead????

    blank_screen(draw)

    y = top + 20
    draw.text((display_left, y), "DM6 to SR16 online!", font=_font, fill="#FFFFFF")

    # Status message
    y += 30
    draw.text((display_left, y), status_message, font=_font, fill="#FFFF00")

    # MIDI info
    y += 22
    draw.text((display_left, y), f"{midi_count} MIDI events", font=_font, fill="#FF00FF")

    # Button label
    y = 180
    draw.text((display_left, y), "<--- SHUT DOWN", font=_font, fill="#FFFF00")

    disp.image(image, rotation)


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

        update_display(draw_object, extra_msg, midi_event_count)

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
