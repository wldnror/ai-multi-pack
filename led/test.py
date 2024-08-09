import board
import neopixel
import time

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.1  # LED 밝기 (0.0에서 1.0 사이)

# 각 줄에 할당된 LED 개수
line_led_counts = [50, 30, 30, 30, 30, 50]
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 각 줄의 시작 인덱스 계산
line_start_indices = [sum(line_led_counts[:i]) for i in range(len(line_led_counts))]

# 특정 LED 인덱스를 반환하는 함수 (반전을 고려)
def get_led_index(line, pos):
    if line % 2 == 1:  # 짝수 줄(2, 4, 6)은 반전
        return line_start_indices[line] + (line_led_counts[line] - 1 - pos)
    else:
        return line_start_indices[line] + pos

# 색상 계산 함수
def wheel(pos):
    if pos < 85:
        return (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170:
        pos -= 85
        return (int(255 - pos * 3), 0, int(pos * 3))
    else:
        pos -= 170
        return (0, int(pos * 3), int(255 - pos * 3))

# 무지개 웨이브 효과 함수
def rainbow_wave(wait):
    for j in range(255):
        for line in range(6):
            for i in range(line_led_counts[line]):
                pixel_index = (i * 256 // line_led_counts[line]) + j
                strip[get_led_index(line, i)] = wheel(pixel_index & 255)
        strip.show()
        time.sleep(wait)

# 무지개 웨이브 실행
while True:
    rainbow_wave(0.05)
