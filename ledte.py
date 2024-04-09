import numpy as np
import board
import neopixel
import sounddevice as sd

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D18  # GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 44100  # 오디오 샘플링 레이트
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

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    for i in range(5):  # 5개 줄에 대한 처리
        brightness = int(np.clip(fft_results[i] / FFT_SIZE * 2, 0, 1) * 255)
        color = tuple(brightness * np.array(COLORS[i]) // 255)
        for j in range(30):
            strip[i * 30 + j] = color
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    if any(indata):
        fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
        fft_result = np.average(np.split(fft_result, 5), axis=1)  # 5개 대역으로 분할
        control_leds(fft_result)

# 메인 함수
def main():
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE):
        print("Streaming started...")
        sd.sleep(-1)  # 무한 대기

if __name__ == "__main__":
    main()
