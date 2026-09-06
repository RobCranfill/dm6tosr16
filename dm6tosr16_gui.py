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

from PIL import Image, ImageDraw, ImageFont

import board
import digitalio
from adafruit_rgb_display import st7789

# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# FONT_PATH = "fonts/upheaval.ttf"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

print(f"{sys.argv[0]} starting up...")

# Main Event Loop pause time; TODO: needed?
MEL_WAIT = 0.5

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
draw = ImageDraw.Draw(image)

# Display constants
x = 0
top = -2

# Load a TrueType font.
font = ImageFont.truetype(FONT_PATH, 24)

# Turn on the _backlight
_backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
_backlight.switch_to_output()
_backlight.value = True


button24 = digitalio.DigitalInOut(board.D24)
button24.direction = digitalio.Direction.INPUT
button24.pull = digitalio.Pull.UP


# IP isn't gonna change! only need to do this once.
cmd = "hostname -I | cut -d' ' -f1"
status_ip = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")

# For reboot function.
count = REBOOT_COUNT
button_was_pushed = False

# Status message at bottom of screen
extra_msg = ""

# Main event loop. Catch exceptions and either restart and keep going, or die.
#
while _keep_running :

    try:

        extra_msg = ""

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
                    # Won't work if run in user space, but OK as service?
                    os.system("shutdown -h now")
                    time.sleep(60) # TODO: needed? useful?
            button_was_pushed = True
        else:
            if button_was_pushed:
                extra_msg = "Shutdown aborted."
                print(extra_msg)
                button_was_pushed = False
                count = REBOOT_COUNT


        # TODO: is this the best way to display this? Can I use labels instead????

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, WIDTH, HEIGHT), outline=0, fill=0)

        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load

        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        status_cpu = subprocess.check_output(cmd, shell=True).decode("utf-8")

        cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        status_mem = subprocess.check_output(cmd, shell=True).decode("utf-8")

        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        status_disk = subprocess.check_output(cmd, shell=True).decode("utf-8")

        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"
        status_temp = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Write four lines of text.
        y = top
        draw.text((x, y), status_ip, font=font, fill="#FFFFFF")

        yh = 22
        y += yh
        draw.text((x, y), status_cpu, font=font, fill="#FFFF00")

        y += yh
        draw.text((x, y), status_mem, font=font, fill="#00FF00")

        y += yh
        draw.text((x, y), status_disk, font=font, fill="#0000FF")

        y += yh
        draw.text((x, y), status_temp, font=font, fill="#FF00FF")

        # Shutdowwn stuff
        y += yh * 4
        draw.text((x, y), "<--- SHUTDOWN", font=font, fill="#FFFF00")

        y += yh
        draw.text((x, y), extra_msg, font=font, fill="#FFFF00")


        # Display the image
        disp.image(image, rotation)
        time.sleep(0.5)

    # TODO: Does ^C get caught here, or does the signal handler get it?
    except KeyboardInterrupt:
        print("\n^C caught; terminating.")
        # backlight_off()
        _keep_running = False

# Done!
backlight_off()
print(f"{sys.argv[0]} dropping out of main event loop.")

