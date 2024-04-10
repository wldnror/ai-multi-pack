import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D18  # GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 44100  # 오디오 샘플레이트
FFT_SIZE = 1024      # FFT 크기, 실제 오디오 데이터의 처리 단위

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
        # fft_results 값을 0에서 255 사이의 값으로 스케일링
        brightness = int(np.clip(fft_results[i] / FFT_SIZE * 2, 0, 1) * 255)
        # 각 줄에 해당하는 색상 선택
        color = tuple(brightness * np.array(COLORS[i]) // 255)
        for j in range(30):  # 각 줄에 30개의 LED
            strip[i * 30 + j] = color
    strip.show()

# 오디오 콜백 함수는 변경하지 않고 유지
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    if np.any(indata):
        fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
        fft_result_split = np.array_split(fft_result, 5)
        fft_result_means = [np.mean(part) for part in fft_result_split]
        control_leds(fft_result_means)

# 메인 함수 내에서
def main():
    # 'default' 오디오 장치를 사용하도록 설정
    default_device = 'default'  # ALSA의 기본 장치를 사용

    with sd.InputStream(callback=audio_callback, channels=2, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device=default_device):
        print("Streaming started...")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()


