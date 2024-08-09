import board
import neopixel
import time

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)

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

# LED 스트립에 글자를 표시하는 함수 (정지된 상태)
def display_static_message():
    # 모든 LED 끄기
    strip.fill((0, 0, 0))
    
    # 'H'와 'E'에 해당하는 LED들 켜기
    # 'H'
    strip[get_led_index(1, 0)] = (255, 255, 255)
    strip[get_led_index(1, 4)] = (255, 255, 255)
    strip[get_led_index(2, 0)] = (255, 255, 255)
    strip[get_led_index(2, 2)] = (255, 255, 255)
    strip[get_led_index(2, 4)] = (255, 255, 255)
    strip[get_led_index(3, 0)] = (255, 255, 255)
    strip[get_led_index(3, 1)] = (255, 255, 255)
    strip[get_led_index(3, 2)] = (255, 255, 255)
    strip[get_led_index(3, 3)] = (255, 255, 255)
    strip[get_led_index(3, 4)] = (255, 255, 255)
    strip[get_led_index(4, 0)] = (255, 255, 255)
    strip[get_led_index(4, 2)] = (255, 255, 255)
    strip[get_led_index(4, 4)] = (255, 255, 255)
    strip[get_led_index(5, 0)] = (255, 255, 255)
    strip[get_led_index(5, 4)] = (255, 255, 255)
    
    # 'E'
    strip[get_led_index(1, 6)] = (255, 255, 255)
    strip[get_led_index(1, 7)] = (255, 255, 255)
    strip[get_led_index(1, 8)] = (255, 255, 255)
    strip[get_led_index(1, 9)] = (255, 255, 255)
    strip[get_led_index(1, 10)] = (255, 255, 255)
    strip[get_led_index(3, 6)] = (255, 255, 255)
    strip[get_led_index(3, 7)] = (255, 255, 255)
    strip[get_led_index(3, 8)] = (255, 255, 255)
    strip[get_led_index(3, 9)] = (255, 255, 255)
    strip[get_led_index(3, 10)] = (255, 255, 255)
    strip[get_led_index(5, 6)] = (255, 255, 255)
    strip[get_led_index(5, 7)] = (255, 255, 255)
    strip[get_led_index(5, 8)] = (255, 255, 255)
    strip[get_led_index(5, 9)] = (255, 255, 255)
    strip[get_led_index(5, 10)] = (255, 255, 255)

    # 글자 표시
    strip.show()

# 메시지 표시 실행
display_static_message()
