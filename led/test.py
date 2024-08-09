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
    ]
}

# 글자 패턴을 LED 스트립에 매핑하는 함수
def map_pattern_to_strip(chars):
    # 빈 매트릭스 생성
    mapped_strip = [[0]*max(line_led_counts) for _ in range(6)]
    
    for idx, char in enumerate(chars):
        if char in FONT:
            pattern = FONT[char]
            start_col = idx * 6  # 글자 간격을 고려하여 시작 위치 조정
            
            for i in range(len(pattern)):  # 5줄의 글자 패턴 사용
                row = pattern[i]
                for j in range(len(row)):
                    if row[j] == "1" and start_col + j < max(line_led_counts):
                        mapped_strip[i + 1][start_col + j] = 1  # 각 줄에 1씩 더해 패턴 적용 (첫 줄은 비움)
    
    return mapped_strip

# 정지 상태에서 글자를 표시하는 함수
def display_static_message(message):
    # 메시지를 스트립에 매핑
    combined_strip = map_pattern_to_strip(message)
    
    led_idx = 0
    for line in range(6):
        line_length = line_led_counts[line]
        for j in range(line_length):
            if j < len(combined_strip[line]):
                pixel = combined_strip[line][j]
                strip[led_idx] = (255, 255, 255) if pixel else (0, 0, 0)
            else:
                strip[led_idx] = (0, 0, 0)
            led_idx += 1
    
    strip.show()

# 메시지 정지 상태로 표시
display_static_message("HE")
