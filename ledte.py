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
    (255, 0, 0),    # 빨간색
    (255, 165, 0),  # 주황색
    (255, 255, 0),  # 노란색
    (0, 255, 0),    # 초록색
    (0, 0, 255)     # 파란색
]

# 이전 밝기 상태를 저장할 배열
last_brightness = [0] * 5

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    # 스펙트럼의 최대값을 찾아 정규화 진행
    max_fft = max(fft_results)
    for i in range(5):
        brightness = int(np.clip((fft_results[i] / max_fft) * 255, 0, 255))
        # 반응 속도 조절: 새 밝기가 더 낮다면 천천히 감소
        if brightness < last_brightness[i]:
            brightness = int(last_brightness[i] * 0.9)  # 이전 밝기의 90%로 감소
        last_brightness[i] = brightness
        color = tuple(brightness * np.array(COLORS[i]) // 255)
        for j in range(30):
            strip[i * 30 + j] = color
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
    fft_result_split = np.array_split(fft_result, 5)
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
