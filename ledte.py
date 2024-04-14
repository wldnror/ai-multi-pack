import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 150
LED_PIN = board.D21
LED_BRIGHTNESS = 0.5
SAMPLE_RATE = 48000
FFT_SIZE = 1024

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_val = np.max(fft_results) if np.max(fft_results) != 0 else 1
    scaled_fft = 255 * (fft_results / max_val)  # 결과를 0~255 범위로 스케일
    num_bands = 10  # 더 세분화된 대역
    leds_per_band = LED_COUNT // num_bands

    for i in range(num_bands):
        hue = int(120 * scaled_fft[i] / 255)  # Hue 값을 120에서 0으로 (초록에서 빨강으로)
        brightness = int(scaled_fft[i])
        color = hsv_to_rgb(hue, 255, brightness)
        for j in range(leds_per_band):
            strip[i * leds_per_band + j] = color
    strip.show()

def hsv_to_rgb(h, s, v):
    h = float(h)
    s = float(s) / 255.0
    v = float(v) / 255.0
    h_i = int(h / 60.0) % 6
    f = (h / 60.0) - h_i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][h_i]
    return (int(r * 255), int(g * 255), int(b * 255))

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
    fft_result_split = np.array_split(fft_result, 10)
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)

def main():
    loopback_device = 'default'
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device='hw:2,1'):
        print("Streaming started...")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
