import datetime
import random

import tkinter as tk

from framework import Pixel, WrappedDisplay, Animation as BaseAnimation


class SimulatorStrand:
    def __init__(self, rows, cols):
        self._led_data = [0] * (rows * cols)

    def show(self):
        pass


class SimulatorDisplay(WrappedDisplay):
    def __init__(self, rows, cols):
        # supply some default, useless gpio_pin value.
        super().__init__(rows, cols, 18)

    def setup_strand(self, gpio_pin, pixel_count, led_frequency, dma,
                     initial_brightness, invert, channel):
        self.strand = SimulatorStrand(self.num_rows, self.num_cols)

    def setup(self, rows, cols):
        return [SimulatorPixel(idx) for idx in range(rows * cols)]


class SimulatorPixel(Pixel):
    def render(self):
        brightness_vector = self.brightness / 255
        red = int(self.red * brightness_vector)
        green = int(self.green * brightness_vector)
        blue = int(self.blue * brightness_vector)
        return f'#{red:02x}{green:02x}{blue:02x}'


class BlinkingAnimation(BaseAnimation):
    def setup(self):
        self.brightness = 0
        self.total_time = 0
        self.row = 0
        self.col = 0
        self.brightness_vector = 10

    def update(self, display, delta):
        self.total_time += delta.total_seconds()
        display.clear()
        p = display.pixel_at(self.row, self.col)
        p.brightness = self.brightness
        p.blue = 255

        self.brightness += self.brightness_vector
        if self.brightness > 255:
            self.brightness = 255
            self.brightness_vector = -self.brightness_vector
        elif self.brightness < 0:
            self.brightness = 0
            self.brightness_vector = -self.brightness_vector
            self.new_pixel(display)

    def new_pixel(self, display):
        self.row = random.randint(0, display.num_rows - 1)
        self.col = random.randint(0, display.num_cols - 1)

    def is_done(self):
        return self.total_time > 30


class OtherAnimation(BaseAnimation):
    def setup(self):
        self.row = 0
        self.col = 0
        self.vector = (1, 1)
        self.time_elapsed = 0
        self.total_time = 0

    def update(self, display, delta):
        seconds = delta.total_seconds()
        self.time_elapsed += seconds
        self.total_time += seconds
        if self.time_elapsed < 0.3:
            return
        self.time_elapsed = 0

        display.clear()
        p = display.pixel_at(self.row, self.col)
        p.brightness = 255
        p.blue = 255

        self.row += self.vector[0]
        self.col += self.vector[1]

        if self.row > display.num_rows - 1:
            self.row = display.num_rows - 1
            self.vector = -self.vector[0], self.vector[1] + random.randint(-1, 1)
        elif self.row < 0:
            self.row = 0
            self.vector = -self.vector[0], self.vector[1] + random.randint(-1, 1)

        if self.col > display.num_cols - 1:
            self.col = display.num_cols - 1
            self.vector = self.vector[0] + random.randint(-1, 1), -self.vector[1]
        elif self.col < 0:
            self.col = 0
            self.vector = self.vector[0] + random.randint(-1, 1), -self.vector[1]

        if self.vector == (0, 0):
            self.vector = random.randint(-1, 1), random.randint(-1, 1)

        if self.vector[0] > 2:
            self.vector = 2, self.vector[1]
        elif self.vector[0] < -2:
            self.vector = -2, self.vector[1]

        if self.vector[1] > 2:
            self.vector = self.vector[0], 2
        elif self.vector[1] < -2:
            self.vector = self.vector[0], -2

    def is_done(self):
        return self.total_time > 30


class App(tk.Tk):
    def __init__(self, animations, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.canvas = tk.Canvas(self, width=500, height=500, borderwidth=0,
                                highlightthickness=0)
        self.canvas.pack(side="top", fill="both", expand="true")
        self.canvas.config({'bg': '#000'})
        self.rows = 7
        self.columns = 7
        self.cellwidth = 500 // 7
        self.cellheight = 500 // 7

        self._animations = animations
        self.display = SimulatorDisplay(self.rows, self.columns)
        self.tick_rate = 10

        self.oval = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column * self.cellwidth
                y1 = row * self.cellheight
                x2 = x1 + self.cellwidth
                y2 = y1 + self.cellheight
                self.oval[row, column] = self.canvas.create_oval(
                    x1 + 2,
                    y1 + 2,
                    x2 - 2,
                    y2 - 2,
                    fill="blue",
                    tags="oval"
                )

        self.canvas.itemconfig("rect", fill="#000")
        self.canvas.itemconfig("oval", fill="#000")
        self.last_time = datetime.datetime.now()
        self.animations = self.get_current_animation()
        self.tick()

    def get_current_animation(self):
        while True:
            for animation in self._animations:
                animation.setup()
                while not animation.is_done():
                    yield animation

    def tick(self):
        animation = next(self.animations)

        now = datetime.datetime.now()

        animation.update(self.display, now - self.last_time)
        for row, col, pixel in self.display.itergrid():
            item_id = self.oval[row, col]
            self.canvas.itemconfig(item_id, fill=pixel.render())
        self.last_time = now

        self.after(self.tick_rate, self.tick)


if __name__ == "__main__":
    app = App([OtherAnimation(), BlinkingAnimation()])
    app.mainloop()
