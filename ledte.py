import numpy as np
import board
import neopixel

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D18  # GPIO 핀 번호 (라즈베리 파이에 맞게 조정하세요)
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    # FFT 결과를 기반으로 LED의 밝기 설정
    for i in range(5):  # 5개의 줄로 가정
        # brightness 값을 0에서 255 사이의 정수로 스케일링
        brightness = int(fft_results[i] * 255)
        for j in range(30):  # 각 줄에 30개의 LED
            # LED 색상 설정 (여기서는 RGB를 같은 값으로 설정하여 밝기만 조절)
            strip[i * 30 + j] = (brightness, brightness, brightness)
    strip.show()

# 메인 함수
def main():
    while True:
        # 실제 응용에서는 여기서 실시간 오디오 데이터를 FFT 분석
        # 여기에서는 시뮬레이션을 위해 임의의 FFT 결과 생성
        fake_fft_results = np.random.rand(5)  # 5개 줄에 대한 가짜 FFT 결과
        control_leds(fake_fft_results)

if __name__ == "__main__":
    main()
