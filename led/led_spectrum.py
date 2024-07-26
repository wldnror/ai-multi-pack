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
band_led_counts = [25, 15, 15, 15, 15, 25]
total_bands = len(band_led_counts)

# 민감도 조정 값
sensitivity_multiplier = [1.0, 1.2, 1.4, 1.4, 1.2, 1.0]

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 무지개 색상 정의
RAINBOW_COLORS = [
    (255, 0, 0),    # 빨간색
    (255, 127, 0),  # 주황색
    (255, 255, 0),  # 노란색
    (0, 255, 0),    # 초록색
    (0, 0, 255),    # 파란색
    (75, 0, 130),   # 남색
    (148, 0, 211)   # 보라색
]

# 스펙트럼 대역을 무지개 색상에 매핑
COLORS = [RAINBOW_COLORS[i % len(RAINBOW_COLORS)] for i in range(total_bands)]

# 무지개 패턴을 표시하는 함수
def show_rainbow(position):
    for i in range(LED_COUNT):
        strip[i] = RAINBOW_COLORS[(i + position) % len(RAINBOW_COLORS)]
    strip.show()

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    half_led_count = LED_COUNT // 2
    center_index = half_led_count - 1
    any_signal = False
    
    for i, count in enumerate(band_led_counts):
        # 민감도 조정 및 로그 스케일 적용
        adjusted_fft_result = np.log1p(fft_results[i] * sensitivity_multiplier[i])
        led_height = int((adjusted_fft_result / np.log1p(max_fft)) * count)
        
        if led_height > 0:
            any_signal = True
        
        # 양쪽으로 퍼지도록 LED 설정
        for j in range(count):
            if j < led_height:
                strip[center_index - j] = COLORS[i]
                strip[center_index + j + 1] = COLORS[i]
            else:
                strip[center_index - j] = (0, 0, 0)
                strip[center_index + j + 1] = (0, 0, 0)
        
        center_index -= count

    if not any_signal:
        global rainbow_position
        show_rainbow(rainbow_position)
        rainbow_position = (rainbow_position + 1) % len(RAINBOW_COLORS)
    
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    # 저주파수 대역에 중점을 둔 FFT 결과 처리
    fft_result = np.abs(np.fft.rfft(indata[:, 0] * np.hanning(indata.shape[0]), n=FFT_SIZE))
    # 주파수 대역 조정 (첫 번째 대역의 주파수 범위를 조정)
    fft_result_split = [
        fft_result[0:20],    # 첫 번째 대역
        fft_result[20:40],   # 두 번째 대역
        fft_result[40:60],   # 세 번째 대역
        fft_result[60:80],   # 네 번째 대역
        fft_result[80:100],  # 다섯 번째 대역
        fft_result[100:120]  # 여섯 번째 대역
    ]
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
