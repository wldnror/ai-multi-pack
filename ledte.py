import numpy as np
import board
import neopixel
import alsaaudio
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

# 오디오 콜백 함수
def audio_callback(data, frame_count, time_info, status):
    if status:
        print("Status:", status)
    if data:
        # FFT 결과 계산
        fft_result = np.abs(np.fft.rfft(np.frombuffer(data, dtype=np.int16), n=FFT_SIZE))
        # np.array_split을 사용하여 5개로 분할
        fft_result_split = np.array_split(fft_result, 5)
        # 각 분할된 결과의 평균을 계산
        fft_result_means = [np.mean(part) for part in fft_result_split]
        control_leds(fft_result_means)

# 메인 함수 내에서
def main():
    # Loopback 장치를 오디오 입력으로 사용
    # ALSA 장치 이름을 직접 지정
    loopback_device = 'hw:Loopback,1,0'  # 선택한 Loopback 장치의 이름

    # ALSA 장치 열기
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, card=loopback_device)
    inp.setchannels(1)
    inp.setrate(SAMPLE_RATE)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(FFT_SIZE)

    print("Streaming started...")
    while True:
        # 데이터 읽기
        _, data = inp.read()
        audio_callback(data, None, None, None)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
