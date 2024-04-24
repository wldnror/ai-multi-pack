import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 256       # LED 개수 (8x32 매트릭스)
LED_PIN = board.D26   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000   # 오디오 샘플레이트
FFT_SIZE = 1024       # FFT 크기
bands_per_column = 32 # 사용할 열의 수

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 각 스펙트럼 대역에 따른 색상 정의
COLORS = [
    (255, 0, 0),    # 빨간색: 저주파수 대역
    (255, 255, 0),  # 노란색: 저-중간 주파수 대역
    (0, 255, 0),    # 초록색: 중간 주파수 대역
    (0, 255, 255),  # 청록색: 중-고주파수 대역
    (0, 0, 255)     # 파란색: 고주파수 대역
]

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    column_height = 8  # 각 열의 높이는 8
    for i in range(bands_per_column):  # 32개 열 처리
        # 로그 스케일 적용
        led_height = int(np.log1p(fft_results[i] / max_fft) * column_height)
        column_index = i * 8
        if i % 2 == 0:  # 짝수 열 (정방향)
            for row in range(column_height):
                strip[column_index + row] = COLORS[i % len(COLORS)] if row < led_height else (0, 0, 0)
        else:  # 홀수 열 (역방향)
            for row in range(column_height):
                strip[column_index + (7 - row)] = COLORS[i % len(COLORS)] if row < led_height else (0, 0, 0)
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    # 저주파수 대역에 중점을 둔 FFT 결과 처리
    fft_result = np.abs(np.fft.rfft(indata[:, 0] * np.hanning(indata.shape[0]), n=FFT_SIZE))
    # 주파수 대역 조정
    important_freqs = fft_result[:FFT_SIZE//25]
    fft_result_split = np.array_split(important_freqs, bands_per_column)  # FFT 결과를 32개의 대역으로 분할
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)

# 메인 함수
def main():
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=1024, device='hw:5,1'):
            print("Streaming started...")
            while True:
                time.sleep(1)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
