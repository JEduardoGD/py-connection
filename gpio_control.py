#!/usr/bin/env python3
"""
Raspberry Pi GPIO Controller
----------------------------
A script to turn a specific GPIO pin ON or OFF.
This script intentionally leaves the pin in the specified state after exiting.
Requires the 'RPi.GPIO' library (standard on Raspberry Pi OS).
"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="Control a Raspberry Pi GPIO pin (ON/OFF).")
    parser.add_argument("pin", type=int, help="The GPIO pin number (BCM numbering, e.g., 17)")
    parser.add_argument("state", choices=["on", "off", "1", "0", "high", "low"], type=str.lower, help="State to set the pin to")

    args = parser.parse_args()

    try:
        import RPi.GPIO as GPIO
    except ImportError:
        print("Error: 'RPi.GPIO' library not found. Please run this on a Raspberry Pi or install the library.")
        sys.exit(1)

    try:
        # Use Broadcom (BCM) pin numbering
        GPIO.setmode(GPIO.BCM)
        
        # Suppress warnings if the pin was already configured previously
        GPIO.setwarnings(False)

        # Set pin as a digital output
        GPIO.setup(args.pin, GPIO.OUT)

        # Determine the target state and apply
        if args.state in ["on", "1", "high"]:
            GPIO.output(args.pin, GPIO.HIGH)
            print(f"Success: GPIO {args.pin} is now ON.")
        else:
            GPIO.output(args.pin, GPIO.LOW)
            print(f"Success: GPIO {args.pin} is now OFF.")
            
        # Note: We intentionally DO NOT call GPIO.cleanup() here.
        # Calling cleanup() would reset the pin back to its default (input/floating) state when the script exits.
        # By omitting it, the pin maintains its HIGH/LOW state.

    except Exception as e:
        print(f"Error controlling GPIO {args.pin}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
