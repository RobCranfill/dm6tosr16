'''
    A display object for the Adafruit PiTFT 1.3" 240x240 display.
    Uses PIL, so only runs on Raspberry Pi Zero and better.
'''

import os

import board
import digitalio
from adafruit_rgb_display import st7789

# Python Image Library
from PIL import Image, ImageDraw, ImageFont


# Configuration for Adafruit 1.3" 240x240 TFT
CS_PIN = digitalio.DigitalInOut(board.CE0)
DC_PIN = digitalio.DigitalInOut(board.D25)
RESET_PIN =  None
HEIGHT = 240
WIDTH = 240
BAUDRATE = 64000000

# Display constants
LEFT_EDGE = 0
TOP_EDGE = -2

BACKLIGHT_PIN = board.D22


# Some other nice fonts to try: http://www.dafont.com/bitmap.php
FONT_PATH = "fonts/upheaval.ttf"
FONT_SIZE = 30
# FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# FONT_SIZE = 24

# Some constant string labels.
TITLE_STRING = "DM6 to SR16"
REBOOT_STRING = "<--- SHUT DOWN"


class tft_display():
    """Nice wrapper for using an Adafruit 1.3" 240x240 TFT display."""

    def __init__(self):
        """Create the display.
        TODO: Pass in font to use? Rotation?
        """

        self._is_running = True

        # Init the ST7789 hardware.
        self._display = st7789.ST7789(
            board.SPI(),
            cs=CS_PIN,
            dc=DC_PIN,
            rst=RESET_PIN,
            baudrate=BAUDRATE,
            width=WIDTH,
            height=HEIGHT,
            x_offset=0,
            y_offset=80 # magic number :-/
            )

        # Create a blank image for drawing.
        # Use 'RGB' for full color.
        self._image = Image.new("RGB", (WIDTH, HEIGHT))
        self._rotation = 180 # buttons on the left - USB connectors down/forward on RPi.

        # Get drawing object to draw on image.
        self._draw_object = ImageDraw.Draw(self._image)

        # Load a TrueType font.
        self._font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        self._backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
        self._backlight.switch_to_output()
        self._backlight.value = True # and turn it on

        print(f"Created display {__name__}")


    def backlight_on(self, turn_on):
        """Set on/off status of the backlight"""
        self._backlight.value = turn_on

    
    def blank_screen(self):
        """Clear the data off the screen.
        # TODO: this doesn't really work? seems to persist across re-starts. ???
        """
        # Draw a black filled box to clear the image.
        self._draw_object.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill="#000000")


    def update(self, uptime, midi_count, status_message):

        # print(f"{uptime=}\n{midi_count=}\n{status_message=}\n")le

        # TODO: This is rather primitive but that's PIL, I guess.

        self.blank_screen()

        y = TOP_EDGE + FONT_SIZE
        self._draw_object.text((LEFT_EDGE, y), TITLE_STRING, font=self._font, fill="#FFFFFF")

        # Uptime
        y += FONT_SIZE
        self._draw_object.text((LEFT_EDGE, y), uptime, font=self._font, fill="#FFFF00")

        # MIDI info
        y += 2 * FONT_SIZE
        self._draw_object.text((LEFT_EDGE, y), f"{midi_count} MIDI events", font=self._font, fill="#FF00FF")

        # Button label
        y = 180
        self._draw_object.text((LEFT_EDGE, y), REBOOT_STRING, font=self._font, fill="#FFFF00")

        # Status message, if any.
        if status_message is not None:
            y += FONT_SIZE
            self._draw_object.text((LEFT_EDGE, y), status_message, font=self._font, fill="#FFFF00")

        self._display.image(self._image, self._rotation)
