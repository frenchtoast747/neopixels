from __future__ import division

import math


class Display(object):
    """
    Args:
        gpio_pin (int): which GPIO pin the data should be sent on.
                        Note: this is not the physical pin number
                        nor the WiringPi number.

    Keyword Args:
        led_frequency (int): the frequency of the LED strand (hertz)
        dma (int): the DMA channel to use for generating the signal. DO NOT
                   use 5 on the Pi 3 as this has been known to corrupt files.
        initial_brightness (int): the initial brightness setting of the LEDs.
                                  should be a value between 0 and 255.
        invert (bool): Set to ``True`` to invert the signal (when using NPN
                       transistor level shift)
        channel (int): set to ``1`` for GPIOs 13, 19, 41, 45, or 53
    """
    def __init__(self, rows, cols, gpio_pin, led_frequency=800000, dma=10,
                 initial_brightness=255, invert=False, channel=0):
        self.initial_brightness = initial_brightness
        self.pixels = self.setup(rows, cols)

        pixel_count = len(self.pixels)
        self.count = pixel_count
        self.num_rows = rows
        self.num_cols = cols

        for pixel in self.pixels:
            pixel.brightness = initial_brightness

        self.strand = None
        self.setup_strand(
            gpio_pin, pixel_count, led_frequency, dma, initial_brightness,
            invert, channel
        )

    def setup(self, rows, cols):
        raise NotImplementedError()

    def setup_strand(self, gpio_pin, pixel_count, led_frequency, dma,
                     initial_brightness, invert, channel):
        from neopixel import Adafruit_NeoPixel
        self.strand = Adafruit_NeoPixel(
            pixel_count,
            gpio_pin,
            led_frequency,
            dma,
            invert,
            initial_brightness,
            channel
        )
        self.strand.begin()

    def fill(self, red, green, blue, brightness=255):
        for pixel in self.pixels:
            pixel.red = red
            pixel.green = green
            pixel.blue = blue
            pixel.brightness = brightness

    def pixel_at(self, row, column):
        return self.pixels[row * self.num_rows + column]

    def show(self):
        for pixel in self.pixels:
            self.strand._led_data[pixel.id] = pixel.render()
        self.strand.show()

    def clear(self):
        for pixel in self.pixels:
            pixel.clear()

        self.show()

    def itergrid(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                yield row, col, self.pixel_at(row, col)


class WrappedDisplay(Display):
    def setup(self, rows, cols):
        pixels = []
        for row_idx in range(rows):
            is_reversed = row_idx % 2 != 0
            for col_idx in range(cols):
                if is_reversed:
                    idx = ((row_idx + 1) * rows) - col_idx - 1
                else:
                    idx = (row_idx * rows) + col_idx
                pixels.append(Pixel(idx))

        return pixels


class Pixel(object):
    def __init__(self, idx):
        self.id = idx
        self.brightness = 255
        self.clear()

    def render(self):
        brightness_vector = self.brightness / 255
        return (
            (int(self.white * brightness_vector) << 24) |
            (int(self.red * brightness_vector) << 16) |
            (int(self.green * brightness_vector) << 8) |
            int(self.blue * brightness_vector)
        )

    def clear(self):
        self.red = 0
        self.green = 0
        self.blue = 0
        self.white = 0


class Animation:
    def update(self, display, delta):
        raise NotADirectoryError()

    def is_done(self):
        raise NotImplementedError()
