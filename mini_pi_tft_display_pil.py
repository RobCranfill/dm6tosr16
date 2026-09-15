'''
Use PIL for display.
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
display_left = 0
top = -2

BACKLIGHT_PIN = board.D22


# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# FONT_PATH = "fonts/upheaval.ttf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


class tft_display():

    def __init__(self):

        self._is_running = True

        # Init the ST7789 display.
        self._display = st7789.ST7789(
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
        self._image = Image.new("RGB", (WIDTH, HEIGHT))
        self._rotation = 180 # buttons on the left - USB connectors down/forward on RPi.

        # Get drawing object to draw on image.
        self._draw_object = ImageDraw.Draw(self._image)

        # Load a TrueType font.
        self._font = ImageFont.truetype(FONT_PATH, 24)

        self._backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
        self._backlight.switch_to_output()
        self._backlight.value = True # and turn it on

        print(f"Created display {__name__}")


    def backlight_on(self, turn_on):
        """Set on/off status of the backlight"""
        self._backlight.value = turn_on


    # TODO: this doesn't really work? seems to persist... sometimes?
    def blank_screen(self):

        # Draw a black filled box to clear the image.
        self._draw_object.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)


    def update(self, uptime, midi_count, status_message):

        # print(f"{uptime=}\n{midi_count=}\n{status_message=}\n")

        # TODO: This is rather primitive but that's PIL, I guess.

        self.blank_screen()

        y = top + 20
        self._draw_object.text((display_left, y), "DM6 to SR16", font=self._font, fill="#FFFFFF")

        # Uptime
        y += 30
        self._draw_object.text((display_left, y), uptime, font=self._font, fill="#FFFF00")

        # Status message
        y += 22
        self._draw_object.text((display_left, y), status_message, font=self._font, fill="#FFFF00")

        # MIDI info
        y += 22
        self._draw_object.text((display_left, y), f"{midi_count} MIDI events", font=self._font, fill="#FF00FF")

        # Button label
        y = 180
        self._draw_object.text((display_left, y), "<--- SHUT DOWN", font=self._font, fill="#FFFF00")

        self._display.image(self._image, self._rotation)
