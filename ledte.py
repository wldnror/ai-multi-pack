import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D21  # GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000  # 오디오 샘플레이트
FFT_SIZE = 1024      # FFT 크기

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 각 스펙트럼 대역에 따른 색상 정의
COLORS = [
    (255, 0, 0),  # 빨간색: 저주파수 대역
    (255, 255, 0),  # 노란색: 저-중간 주파수 대역
    (0, 255, 0),    # 초록색: 중간 주파수 대역
    (0, 255, 255),  # 청록색: 중-고주파수 대역
    (0, 0, 255)     # 파란색: 고주파수 대역
]

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    for i in range(5):  # 5개의 스펙트럼 대역 처리
        led_height = int((fft_results[i] / max_fft) * 30)
        for j in range(30):
            if j < led_height:
                strip[i * 30 + j] = COLORS[i]
            else:
                strip[i * 30 + j] = (0, 0, 0)
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    fft_result = np.abs(np.fft.rfft(indata[:, 0] * np.hanning(indata.shape[0]), n=FFT_SIZE))
    fft_mid_range = fft_result[len(fft_result)//4:len(fft_result)*3//4]  # 중간 주파수 대역만 사용
    fft_result_split = np.array_split(fft_mid_range, 5)  # 중간 범위를 5개로 나눔
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)

# 메인 함수
def main():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device='hw:2,1'):
        print("Streaming started...")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
