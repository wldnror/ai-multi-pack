import numpy as np
import board
import neopixel
import sounddevice as sd
import time
import random

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)
SAMPLE_RATE = 48000   # 오디오 샘플레이트
FFT_SIZE = 1024       # FFT 크기

# 각 스펙트럼 대역에 할당된 LED 개수
band_led_counts = [50, 30, 30, 30, 30, 50]
total_bands = len(band_led_counts)

# 민감도 조정 값 (첫 번째와 마지막 대역의 민감도는 조금 더 낮게 설정)
sensitivity_multiplier = [1.0, 1.2, 1.4, 1.4, 1.2, 1.0]

# 지수 평활화 계수 (첫 번째 대역)
alpha = 0.1

# 지수 평활화된 결과를 저장할 변수 초기화
smoothed_fft = [0] * total_bands

# 색상 변경 카운터 초기화
change_counters = [0] * total_bands

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 지정된 색상 팔레트 (빨, 주, 노, 초, 파, 남, 보)
COLOR_PALETTE = [
    (255, 0, 0),     # 빨강
    (255, 165, 0),   # 주황
    (255, 255, 0),   # 노랑
    (0, 255, 0),     # 초록
    (0, 0, 255),     # 파랑
    (0, 0, 128),     # 남색
    (128, 0, 128)    # 보라
]

# 초기 색상 설정 (서로 겹치지 않도록)
COLORS = random.sample(COLOR_PALETTE, total_bands)

# 부드러운 무지개 패턴을 표시하는 함수
def show_rainbow(position):
    for i in range(LED_COUNT):
        pixel_index = (i * 512 // LED_COUNT) + position
        strip[i] = wheel(pixel_index & 255)
    strip.show()

# 무지개 효과를 위한 색상 선택 함수
def wheel(pos):
    """Input a value 0 to 255 to get a color value.
    The colors are a transition r - g - b - back to r."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

# 랜덤 색상 선택 함수 (다른 대역과 중복되지 않도록)
def pick_random_color(exclude_colors):
    available_colors = [color for color in COLOR_PALETTE if color not in exclude_colors]
    return random.choice(available_colors)

# FFT 결과에 따라 LED 제어하는 함수
def control_leds(fft_results):
    global COLORS  # 전역 변수로 선언
    global rainbow_position
    global last_signal_time

    max_fft = max(fft_results) if max(fft_results) != 0 else 1
    led_index = 0
    any_signal = False
    used_colors = []

    for i, count in enumerate(band_led_counts):
        if i == 0:
            smoothed_fft[i] = alpha * fft_results[i] + (1 - alpha) * smoothed_fft[i]
            adjusted_fft_result = np.log1p(smoothed_fft[i] * sensitivity_multiplier[i])
        else:
            adjusted_fft_result = np.log1p(fft_results[i] * sensitivity_multiplier[i])
        
        led_height = int((adjusted_fft_result / np.log1p(max_fft)) * count)
        
        if led_height > 0:
            any_signal = True
        
        # 이전 LED 높이와 비교하여 줄어들 때 카운터 증가
        if led_height < smoothed_fft[i]:
            change_counters[i] += 1
        
        # 두 번의 변화가 발생한 경우에만 색상 변경
        if change_counters[i] >= 5:
            COLORS[i] = pick_random_color(used_colors)
            change_counters[i] = 0  # 카운터 초기화
        
        smoothed_fft[i] = led_height  # 현재 높이를 저장하여 다음에 비교할 수 있게 함
        used_colors.append(COLORS[i])  # 사용된 색상 목록에 추가
        
        if i % 2 == 1:  # 두 번째, 네 번째, 여섯 번째 대역 반전
            for j in range(count):
                if j < led_height:
                    strip[led_index + count - 1 - j] = COLORS[i]
                    strip[LED_COUNT - 1 - (led_index + count - 1 - j)] = COLORS[i]  # 대칭 적용
                else:
                    strip[led_index + count - 1 - j] = (0, 0, 0)
                    strip[LED_COUNT - 1 - (led_index + count - 1 - j)] = (0, 0, 0)
        else:
            for j in range(count):
                if j < led_height:
                    strip[led_index + j] = COLORS[i]
                    strip[LED_COUNT - 1 - (led_index + j)] = COLORS[i]  # 대칭 적용
                else:
                    strip[led_index + j] = (0, 0, 0)
                    strip[LED_COUNT - 1 - (led_index + j)] = (0, 0, 0)
        
        led_index += count
    
    # 사운드 신호가 없으면 무지개 효과를 활성화
    current_time = time.time()
    if any_signal:
        last_signal_time = current_time
    elif current_time - last_signal_time >= 0.5:
        show_rainbow(rainbow_position)
        rainbow_position = (rainbow_position + 1) % 512
    
    strip.show()

# 오디오 콜백 함수
def audio_callback(indata, frames, time, status):
    if status:
        print("Status:", status)
    # 저주파수 대역에 중점을 둔 FFT 결과 처리
    fft_result = np.abs(np.fft.rfft(indata[:, 0] * np.hanning(indata.shape[0]), n=FFT_SIZE))
    # 주파수 대역 조정
    important_freqs = fft_result[:FFT_SIZE//25]
    fft_result_split = np.array_split(important_freqs, total_bands)  # FFT 결과를 각 대역에 맞게 분할
    fft_result_means = [np.mean(part) for part in fft_result_split]
    control_leds(fft_result_means)

# 전역 변수 초기화
rainbow_position = 0
last_signal_time = time.time()

# 메인 함수
def main():
    try:
        with sd.InputStream(callback=audio_callback, channels=1, samplerate=SAMPLE_RATE, blocksize=1024):
            print("Streaming started...")
            while True:
                time.sleep(0.1)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
