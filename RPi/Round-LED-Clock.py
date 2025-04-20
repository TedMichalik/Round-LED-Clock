#!/usr/bin/env python3
# Author: Ted Michalik (ted@tedmichalik.com)
# Mashup of the following programs to control a Round-LED-Clock with a Raspberry Pi Zero W.
#
# Author: Leon van den Beukel
# Direct port of Round-LED-Clock.ino
# Author: Tony DiCola (tony@tonydicola.com)
# Direct port of the Arduino NeoPixel library strandtest example.
# Author: BlackberryJamMan
# https://www.instructables.com/Desktop-Equinox-Clock/

import time
from datetime import datetime
from rpi_ws281x import *
import argparse

# LED strip configuration:
LED_COUNT      = 60     # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
#LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_FREQ_HZ    = 1250000 # LED signal frequency in hertz (for SPI 1.25 mhz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_OFFSET     = 30      # Position of first LED: 0 = 12 o'clock; 30 = 6 0'clock

# Change the colors here if you want.
colorHour = Color(255,   0,   0) # Red
colorMinute = Color(  0, 255,   0) # Green
colorSecond = Color(  0,   0, 255) # Blue
colorHourMinute = Color(255, 255,   0) # Yellow
colorHourSecond = Color(255,   0, 255) # Magenta
colorMinuteSecond = Color(  0, 255, 255) # Cyan
colorAll = Color(255, 255, 255) # White
colorNone = Color(  0,   0,   0) # Black

# Set this to True if you want the hour LED to move between hours (if set to False the hour LED will only move every hour)
USE_LED_MOVE_BETWEEN_HOURS = True

# Cutoff times for day / night brightness.
USE_NIGHTCUTOFF = False   # Enable/Disable night brightness
MORNINGCUTOFF = 8         # When does daybrightness begin?   8am
NIGHTCUTOFF = 20          # When does nightbrightness begin? 8pm
NIGHTBRIGHTNESS = 20      # Brightness level from 0 (off) to 255 (full brightness)

# Define functions which animate LEDs in various ways.
def all_LEDs_off(strip):
    """Turn off all LEDs."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, colorNone)
        strip.show()

def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def quarter_chime(strip, n):
    all_LEDs_off(strip)
    startLED = (n - 15 + LED_OFFSET) % strip.numPixels()
    endLED = startLED + 15
    for j in range(3):
        for i in range(startLED, endLED):
            strip.setPixelColor(i, colorAll)
        strip.show()
        time.sleep(0.3)
        all_LEDs_off(strip)
        time.sleep(0.3)

def o_clock_chime(strip):
    all_LEDs_off(strip)
    colorWipe(strip, colorAll)
    for j in range(3):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, colorAll)
        strip.show()
        time.sleep(0.3)
        all_LEDs_off(strip)
        time.sleep(0.3)

def theaterChase(strip, c):
    for j in range(10):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, c)
            strip.show()
            time.sleep(0.3)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, colorNone)

def Wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip):
    for j in range(256):
        for i in range(0, strip.numPixels()):
            strip.setPixelColor(i, Wheel((i+j) & 255))
        strip.show()
        time.sleep(0.02)

def rainbowCycle(strip):
    for j in range(256*5):
        for i in range(0, strip.numPixels()):
            strip.setPixelColor(i, Wheel(((int(i * 256 / strip.numPixels()) + j) & 255)))
        strip.show()
        time.sleep(0.02)

def theaterChaseRainbow(strip):
    for j in range(0, 256, 8 ):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, Wheel((i+j) % 255))
            strip.show()
            time.sleep(0.3)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, colorNone)

def GetLEDHour(hours, minutes):
    """Get LED number for the hour."""
    hourLED = ((hours * 5) + LED_OFFSET) % strip.numPixels()

    if (USE_LED_MOVE_BETWEEN_HOURS):
        if (minutes >= 12 and minutes < 24): hourLED += 1;
        elif (minutes >= 24 and minutes < 36): hourLED += 2;
        elif (minutes >= 36 and minutes < 48): hourLED += 3;
        elif (minutes >= 48): hourLED += 4

    return hourLED

def getLEDMinuteOrSecond(minuteOrSecond):
    """Get LED number for the minute or second."""
    minuteOrSecond = (minuteOrSecond + LED_OFFSET) % strip.numPixels()
    return minuteOrSecond

def night():
    """Return True if nighttime"""
    hr = datetime.now().hour
    if (hr < MORNINGCUTOFF or hr >= NIGHTCUTOFF): return True
    else: return False

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-d', '--debug', action='store_true', help='print debugging messages')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    last = 0
    lasthr = 0
    lastmin = 0

    if args.debug: print ('Press Ctrl-C to quit.')
    if args.debug: print ('Set hands.')
    if not args.clear:
        if args.debug: print('Use "-c" argument to clear LEDs on exit')

    colorWipe(strip, colorAll)
    colorWipe(strip, colorNone)

    try:

        while True:
            second = getLEDMinuteOrSecond(datetime.now().second)
            if (second != last):
                minute = getLEDMinuteOrSecond(datetime.now().minute)
                hour = GetLEDHour(datetime.now().hour, datetime.now().minute)
                if args.debug: print (hour, ':', minute, ':', second)
 
                # Lightshows
                if (datetime.now().second == 0):
                    if (datetime.now().minute == 0):
                        colorWipe(strip, colorAll)
                        colorWipe(strip, colorHour)
                        colorWipe(strip, colorMinute)
                        colorWipe(strip, colorSecond)
                        theaterChase(strip, colorAll)
                        rainbow(strip)
                        rainbowCycle(strip)
                        theaterChaseRainbow(strip)
                        o_clock_chime(strip)
                    if (datetime.now().minute == 15):
                        theaterChase(strip, colorAll)
                        quarter_chime(strip, 15)
                    if (datetime.now().minute == 30):
                        colorWipe(strip, colorAll)
                        theaterChaseRainbow(strip)
                        quarter_chime(strip, 30)
                    if (datetime.now().minute == 45):
                        colorWipe(strip, colorAll)
                        rainbowCycle(strip)
                        rainbow(strip)
                        quarter_chime(strip, 45)

                # Clear old spots
                strip.setPixelColor(last, colorNone)  # old second off
                strip.setPixelColor(lastmin, colorNone)  # old hour off
                strip.setPixelColor(lasthr, colorNone)  # old hour off

                # Set hands
                strip.setPixelColor(hour, colorHour)  # Red hour
                strip.setPixelColor(minute, colorMinute)  # Green minute
                strip.setPixelColor(second, colorSecond)  # Blue second

                # Hour and min are on same spot
                if (hour == minute): strip.setPixelColor(hour, colorHourMinute)
                # Hour and sec are on same spot
                if (hour == second): strip.setPixelColor(hour, colorHourSecond)
                # Min and sec are on same spot
                if (minute == second): strip.setPixelColor(minute, colorMinuteSecond)
                # All are on same spot
                if (minute == second and minute == hour):
                    strip.setPixelColor(minute, colorAll)

                if (night() and USE_NIGHTCUTOFF):
                    strip.setBrightness (NIGHTBRIGHTNESS)

                strip.show()
                last = second
                lastmin = minute
                lasthr = hour
            time.sleep(0.1)


    except KeyboardInterrupt: # When 'Ctrl+C' is pressed, execute this code.
        if args.clear:
            colorWipe(strip, colorNone, 10)
