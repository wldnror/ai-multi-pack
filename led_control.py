# led_control.py
import time
import board
import neopixel
import numpy as np

LED_COUNT = 150
LED_PIN = board.D18
LED_BRIGHTNESS = 0.5
COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]

strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

def control_leds(fft_means):
    for i, value in enumerate(fft_means):
        brightness = int(np.clip(value / 2048 * 2, 0, 1) * 255)
        color = tuple(brightness * np.array(COLORS[i]) // 255)
        for j in range(30):
            strip[i * 30 + j] = color
    strip.show()

def read_fft_data():
    try:
        with open('fft_data.txt', 'r') as f:
            return [float(line.strip()) for line in f]
    except FileNotFoundError:
        return [0] * 5

def main():
    while True:
        fft_means = read_fft_data()
        control_leds(fft_means)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
