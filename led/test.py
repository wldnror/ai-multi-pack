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

# 글자 패턴 (5x7 폰트)
FONT = {
    'H': [
        "10001",
        "10001",
        "11111",
        "10001",
        "10001",
    ],
    'E': [
        "11111",
        "10000",
        "11111",
        "10000",
        "11111",
    ],
    'L': [
        "10000",
        "10000",
        "10000",
        "10000",
        "11111",
    ],
    'O': [
        "01110",
        "10001",
        "10001",
        "10001",
        "01110",
    ]
}

# 특정 글자 패턴을 LED 스트립에 매핑
def map_pattern_to_strip(char):
    if char not in FONT:
        return None

    pattern = FONT[char]
    mapped_strip = [[0]*max(line_led_counts) for _ in range(6)]
    
    for i in range(min(len(pattern), 5)):  # 5줄의 글자 패턴 사용
        row = pattern[i]
        for j in range(len(row)):
            if row[j] == "1":
                mapped_strip[i + 1][j] = 1  # 각 줄에 1씩 더해 패턴 적용 (첫 줄은 비움)
    
    return mapped_strip

# 메시지를 스크롤하는 함수
def scroll_message(message, speed=0.1):
    combined_strip = [[0]*sum(line_led_counts) for _ in range(6)]
    
    # 메시지의 각 글자를 스트립에 매핑
    for char in message:
        char_matrix = map_pattern_to_strip(char)
        if char_matrix:
            for i in range(6):
                combined_strip[i] += char_matrix[i] + [0]  # 글자 간의 간격을 추가
    
    # 스크롤 애니메이션
    for offset in range(len(combined_strip[0]) - max(line_led_counts) + 1):
        led_idx = 0
        for line in range(6):
            line_length = line_led_counts[line]
            for j in range(line_length):
                if j + offset < len(combined_strip[line]):
                    pixel = combined_strip[line][j + offset]
                    strip[led_idx] = (255, 255, 255) if pixel else (0, 0, 0)
                else:
                    strip[led_idx] = (0, 0, 0)
                led_idx += 1
        
        strip.show()
        time.sleep(speed)

# 메시지 스크롤 실행
scroll_message("HELLO")
