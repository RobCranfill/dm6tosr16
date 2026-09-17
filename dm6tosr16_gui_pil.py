"""
    dm6tosr16 gui
    See https://github.com/RobCranfill/dm6tosr16
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

# The PIL-based GUI is good enough for now.
import mini_pi_tft_display_pil


print(f"{sys.argv[0]} starting up...")

# Count down from this for reboot:
REBOOT_COUNT = 5


_keep_running = True

# SIGTERM is sent to a service on system shutdown. Handle it.
# We want to turn off the _backlight at least.
def signal_handler(sig, frame):
    print(f"Signal {sig} caught; terminating.")
    # backlight_off()
    _keep_running = False

signal.signal(signal.SIGTERM, signal_handler)


button24 = digitalio.DigitalInOut(board.D24)
button24.direction = digitalio.Direction.INPUT
button24.pull = digitalio.Pull.UP


# Find the right input port to connect to
print("Opening ALSA MIDI input port...")

def find_midi_port(tft, name_or_fragment, look_for_input_not_output):

    in_or_out = "input" if look_for_input_not_output else "output"

    port_to_use = None
    print(f"Looking for MIDI {in_or_out} port '{name_or_fragment}'....")
    while port_to_use is None:

        if look_for_input_not_output:
            ports = mido.get_input_names()
        else:
            ports = mido.get_output_names()

        for port_name in ports:
            if name_or_fragment in port_name:
                port_to_use = port_name
        if port_to_use is None:
            print("  Scanning ports again....")
            display.update("Scanning ports again....", 0, "No DM6 found!")
            time.sleep(2)
    print(f"  Using MIDI port {port_to_use} as {in_or_out}.")
    midi_port = mido.open_input(port_to_use)
    return midi_port


# For reboot function. Count down from this max.
count = REBOOT_COUNT
button_was_pushed = False


display = mini_pi_tft_display_pil.tft_display()
display.blank_screen()

# Status message at bottom of screen
extra_msg = ""

start_time = time.monotonic()
midi_event_count = 0


input_port = find_midi_port(display, "e-drum", True)

# Main event loop. Catch exceptions and either restart and keep going, or die.
#
while _keep_running :

    try:

        # We just want to count the messages.
        for msg in input_port.iter_pending():
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

        # TODO: show uptime in HH:MM:SS ?
        uptime = int(time.monotonic() - start_time)
        hms = time.strftime('%H:%M:%S', time.gmtime(uptime))
        display.update(f"Uptime {hms}", midi_event_count, extra_msg)

        time.sleep(0.2)

    # TODO: Does ^C get caught here, or does the signal handler get it?
    except KeyboardInterrupt:
        print("\n^C caught; terminating.")
        # backlight_off()
        _keep_running = False

# Done!
display.blank_screen()
display.backlight_on(False)
print(f"{sys.argv[0]} dropping out of main event loop.")
