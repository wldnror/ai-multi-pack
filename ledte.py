import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D21# GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000  # 오디오 샘플레이트
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
    for i in range(5):  # 5개 밴드 처리
        # FFT 결과를 로그 스케일로 조정하여 더 넓은 동적 범위를 갖도록 함
        brightness = int(np.clip(10 * np.log10(fft_results[i] + 1), 0, 255))
        color = tuple(brightness * np.array(COLORS[i]) // 255)
        for j in range(30):  # 각 밴드에 30개의 LED
            strip[i * 30 + j] = color
    strip.show()

# 오디오 콜백 함수 내에서 FFT 처리 개선
def audio_callback(indata, frames, time, status):
    fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
    fft_result_split = np.array_split(fft_result, 5)
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)
)

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    print("Input data:", indata)
    if status:
        print("Status:", status)
    if np.any(indata):
        # FFT 결과 계산
        fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
        # np.array_split을 사용하여 5개로 분할
        fft_result_split = np.array_split(fft_result, 5)
        # 각 분할된 결과의 평균을 계산
        fft_result_means = [np.mean(part) for part in fft_result_split]
        control_leds(fft_result_means)

# 메인 함수 내에서
def main():
    # Loopback 장치를 오디오 입력으로 사용
    # 'aplay -L' 또는 'arecord -L' 명령을 사용하여 확인한 실제 가상 마이크의 ALSA 장치 이름
    loopback_device = 'default'  # 'default'는 PulseAudio를 통해 오디오를 가져옵니다.

    # 입력 스트림을 생성하고 콜백 함수로 오디오 데이터 처리
    with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device='hw:2,1'):
        print("Streaming started...")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    main()
