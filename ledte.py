import numpy as np
import board
import neopixel
import sounddevice as sd
import time

# LED 스트립 설정
LED_COUNT = 150      # LED 개수
LED_PIN = board.D18  # GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)
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

# 샘플 속도 확인
def print_device_info():
    print("Available audio devices:")
    for i, dev in enumerate(sd.query_devices()):
        print(f"  {i}: {dev['name']} (input: {dev['max_input_channels']}, output: {dev['max_output_channels']})")
        if dev['name'] == 'loopback_device_name':
            print(f"    Supported sample rates: {dev['supported_samplerates']}")

# 메인 함수 내에서 호출하여 확인
def main():
    print_device_info()  # 샘플 속도 확인을 위해 사용 가능한 오디오 장치 정보를 출력합니다.
    # 선택한 샘플 속도를 설정합니다. 아래의 값을 지원하는 샘플 속도 중 하나로 변경하십시오.
    SAMPLE_RATE = 44100  # 예시로 44100Hz로 설정합니다.
    
    # Loopback 장치를 오디오 입력으로 사용
    loopback_device = 'hw:3,1'  # 루프백 장치의 이름이나 인덱스를 여기에 지정

    # 입력 스트림을 생성하고 콜백 함수로 오디오 데이터 처리
    with sd.InputStream(callback=audio_callback, channels=2, samplerate=SAMPLE_RATE, blocksize=FFT_SIZE, device=loopback_device):
        print("Streaming started...")
        while True:
            time.sleep(1)

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
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    if np.any(indata):
        # FFT 결과 계산
        fft_result = np.abs(np.fft.rfft(indata[:, 0], n=FFT_SIZE))
        # np.array_split을 사용하여 5개로 분할
        fft_result_split = np.array_split(fft_result, 5)
        # 각 분할된 결과의 평균을 계산
        fft_result_means = [np.mean(part) for part in fft_result_split]
        control_leds(fft_result_means)

if __name__ == "__main__":
    main()
