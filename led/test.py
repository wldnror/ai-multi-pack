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

# LED 스트립에 하트 모양을 표시하는 함수 (정지된 상태)
def display_heart():
    # 모든 LED 끄기
    strip.fill((0, 0, 0))
    
    # 하트 모양의 LED들 켜기
    # 첫 번째 줄은 비워둠
    # 두 번째 줄
    strip[get_led_index(1, 9)] = (255, 0, 0)
    strip[get_led_index(1, 10)] = (255, 0, 0)
    strip[get_led_index(1, 12)] = (255, 0, 0)
    strip[get_led_index(1, 13)] = (255, 0, 0)

    # 세 번째 줄
    strip[get_led_index(2, 8)] = (255, 0, 0)
    strip[get_led_index(2, 11)] = (255, 0, 0)
    strip[get_led_index(2, 14)] = (255, 0, 0)
    
    # 네 번째 줄
    strip[get_led_index(3, 7)] = (255, 0, 0)
    strip[get_led_index(3, 15)] = (255, 0, 0)
    
    # 다섯 번째 줄
    strip[get_led_index(4, 8)] = (255, 0, 0)
    strip[get_led_index(4, 14)] = (255, 0, 0)
    
    # 여섯 번째 줄
    strip[get_led_index(5, 9)] = (255, 0, 0)
    strip[get_led_index(5, 10)] = (255, 0, 0)
    strip[get_led_index(5, 11)] = (255, 0, 0)
    strip[get_led_index(5, 12)] = (255, 0, 0)
    strip[get_led_index(5, 13)] = (255, 0, 0)
    
    # 하트 모양 표시
    strip.show()

# 메시지 표시 실행
display_heart()
