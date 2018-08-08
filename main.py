import time
import random

from framework import WrappedDisplay

d = WrappedDisplay(rows=7, cols=7, gpio_pin=18)


def blinkin():
    d.clear()
    while True:
        idx = random.randint(0, 48)
        p = d.pixels[idx]
        p.blue = random.randint(0, 255)
        p.red = random.randint(0, 255)
        p.green = random.randint(0, 255)
        for b in list(range(0, 128, 10)) + list(range(128, 5, -10)):
            p.brightness = b
            d.show()
            time.sleep(0.05)

try:
    blinkin()
except KeyboardInterrupt:
    d.clear()
