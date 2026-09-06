"""
dm6tosr16 gui
 adapted from
    https://learn.adafruit.com/adafruit-mini-pitft-135x240-color-tft-add-on-for-raspberry-pi/python-stats
"""

import subprocess
import time

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont

from adafruit_rgb_display import st7789


THRESHOLD = 5

# Configuration for 1.3" 240x240 TFT
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

BACKLIGHT_PIN = board.D22

# Config for display baudrate (default max is 24mhz)
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI
spi = board.SPI()

# Create the ST7789 display
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=240,
    height=240,
    x_offset=0,
    y_offset=80,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 180

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)

# Turn on the backlight
backlight = digitalio.DigitalInOut(BACKLIGHT_PIN)
backlight.switch_to_output()
backlight.value = True


button24 = digitalio.DigitalInOut(board.D24)
button24.direction = digitalio.Direction.INPUT
button24.pull = digitalio.Pull.UP


# IP isn't gonna change! only need to do this once.
cmd = "hostname -I | cut -d' ' -f1"
status_ip = "IP: " + subprocess.check_output(cmd, shell=True).decode("utf-8")

count = THRESHOLD
button_was_pushed = False

extra_msg = ""


while True:
    
    extra_msg = ""

    button_is_pushed = not button24.value
    if button_is_pushed:
        if not button_was_pushed:
            extra_msg = f"Shutdown in {THRESHOLD}..."
            print(extra_msg)
        else:
            count -= 1
            extra_msg = f"Shutdown in {count}..."
            print(extra_msg)
            if count == 0:
                print("DIE DIE DIE!")
                # os.system("shutdown now -h")
        button_was_pushed = True
    else:
        if button_was_pushed:
            extra_msg = "Shutdown aborted."
            print(extra_msg)
            button_was_pushed = False
            count = THRESHOLD


    # TODO: is this the best way to display this? Can I use labels instead????

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

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
