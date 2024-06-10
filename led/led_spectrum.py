import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000   # 오디오 샘플레이트
FFT_SIZE = 1024       # FFT 크기

# 각 스펙트럼 대역에 할당된 LED 개수
band_led_counts = [50, 30, 30, 30, 30, 50]
total_bands = len(band_led_counts)

# 민감도 조정 값
sensitivity_multiplier = [2.0, 1.0, 1.0, 1.0, 1.0, 2.0]

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 각 스펙트럼 대역에 따른 색상 정의
COLORS = [
    (255, 0, 0),    # 빨간색: 저주파수 대역
    (255, 255, 0),  # 노란색: 저-중간 주파수 대역
    (0, 255, 0),    # 초록색: 중간 주파수 대역
    (0, 255, 255),  # 청록색: 중-고주파수 대역
    (0, 0, 255),    # 파란색: 고주파수 대역
    (255, 0, 255)   # 보라색: 최상위 주파수 대역
]

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    led_index = 0
    for i, count in enumerate(band_led_counts):
        # 민감도 조정
        adjusted_fft_result = fft_results[i] * sensitivity_multiplier[i]
        led_height = int(np.log1p(adjusted_fft_result / max_fft) * count)
        if i % 2 == 1:  # 두 번째, 네 번째, 여섯 번째 대역 반전
            for j in range(count):
                if j < led_height:
                    strip[led_index + count - 1 - j] = COLORS[i]
                else:
                    strip[led_index + count - 1 - j] = (0, 0, 0)
        else:
            for j in range(count):
                if j < led_height:
                    strip[led_index + j] = COLORS[i]
                else:
                    strip[led_index + j] = (0, 0, 0)
        led_index += count
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

# 메인 함수
def main():
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=1024, device='hw:4,0'):
            print("Streaming started...")
            while True:
                time.sleep(1)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
