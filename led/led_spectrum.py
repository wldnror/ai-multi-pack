import numpy as np
import board
import neopixel
import sounddevice as sd
import time
import random

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000   # 오디오 샘플레이트
FFT_SIZE = 1024       # FFT 크기

# 각 스펙트럼 대역에 할당된 LED 개수
band_led_counts = [50, 30, 30, 30, 30, 50]
total_bands = len(band_led_counts)

# 민감도 조정 값 (첫 번째와 마지막 대역의 민감도는 조금 더 낮게 설정)
sensitivity_multiplier = [1.0, 1.2, 1.4, 1.4, 1.2, 1.0]

# 지수 평활화 계수 (첫 번째 대역)
alpha = 0.1

# 지수 평활화된 결과를 저장할 변수 초기화
smoothed_fft = [0] * total_bands

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 부드러운 색상 변화를 위한 색상 정의
def wheel(pos):
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

# 스펙트럼 대역을 무지개 색상에 매핑
COLORS = [wheel(i * 256 // total_bands) for i in range(total_bands)]

# 부드러운 무지개 패턴을 표시하는 함수
def show_rainbow(position):
    for i in range(LED_COUNT):
        pixel_index = (i * 512 // LED_COUNT) + position
        strip[i] = wheel(pixel_index & 255)
    strip.show()

# 주파수 대역의 순서를 랜덤으로 섞는 함수
def shuffle_bands(fft_results):
    band_indices = list(range(total_bands))
    random.shuffle(band_indices)
    shuffled_fft = [fft_results[i] for i in band_indices]
    shuffled_colors = [COLORS[i] for i in band_indices]
    return shuffled_fft, shuffled_colors

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    led_index = 0
    any_signal = False

    # 주파수 대역과 색상을 무작위로 섞음
    shuffled_fft, shuffled_colors = shuffle_bands(fft_results)
    
    for i, count in enumerate(band_led_counts):
        # 첫 번째 대역에 대해 지수 평활화 적용
        if i == 0:
            smoothed_fft[i] = alpha * shuffled_fft[i] + (1 - alpha) * smoothed_fft[i]
            adjusted_fft_result = np.log1p(smoothed_fft[i] * sensitivity_multiplier[i])
        else:
            adjusted_fft_result = np.log1p(shuffled_fft[i] * sensitivity_multiplier[i])
        led_height = int((adjusted_fft_result / np.log1p(max_fft)) * count)
        if led_height > 0:
            any_signal = True
        
        # LED를 해당 대역의 색상으로 켜기
        for j in range(count):
            if j < led_height:
                strip[led_index + j] = shuffled_colors[i]
            else:
                strip[led_index + j] = (0, 0, 0)
        led_index += count

    if not any_signal:
        global rainbow_position
        show_rainbow(rainbow_position)
        rainbow_position = (rainbow_position + 1) % 512
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    # 저주파수 대역에 중점을 둔 FFT 결과 처리
    fft_result = np.abs(np.fft.rfft(indata[:, 0] * np.hanning(indata.shape[0]), n=FFT_SIZE))
    # 주파수 대역 조정
    important_freqs = fft_result[:FFT_SIZE//25]
    fft_result_split = np.array_split(important_freqs, total_bands)  # FFT 결과를 각 대역에 맞게 분할
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)

# 전역 변수 초기화
rainbow_position = 0

# 메인 함수
def main():
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=1024, device='hw:4,1'):
            print("Streaming started...")
            while True:
                time.sleep(0.1)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
