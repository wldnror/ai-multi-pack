import numpy as np
import board
import neopixel
import time

# LED 스트립 설정
LED_COUNT = 220       # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.05 # LED 밝기 (0.0에서 1.0 사이)

# 각 대역에 해당하는 LED 개수
band_led_counts = [50, 30, 30, 30, 30, 50]
total_bands = len(band_led_counts)
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

# 특정 글자 패턴을 6x50 LED 매트릭스에 매핑
def map_pattern_to_matrix(char):
    if char not in FONT:
        return None
    
    pattern = FONT[char]
    mapped_matrix = [[0]*50 for _ in range(6)]
    
    for i in range(min(len(pattern), len(mapped_matrix))):
        row = pattern[i]
        for j in range(len(row)):
            if row[j] == "1":
                mapped_matrix[i][j] = 1
    
    return mapped_matrix

# 문자 스크롤 함수
def scroll_message(message, speed=0.1):
    combined_matrix = [[0]*50 for _ in range(6)]
    
    # 메시지에 있는 각 글자를 매핑
    for char in message:
        char_matrix = map_pattern_to_matrix(char)
        if char_matrix:
            for i in range(6):
                combined_matrix[i] += char_matrix[i] + [0]  # 글자 간격 추가
    
    # 스크롤 애니메이션
    for offset in range(len(combined_matrix[0]) - 50 + 1):
        for band in range(total_bands):
            for j in range(band_led_counts[band]):
                if j + offset < len(combined_matrix[band]):
                    pixel = combined_matrix[band][j + offset]
                    strip[sum(band_led_counts[:band]) + j] = (255, 255, 255) if pixel else (0, 0, 0)
        
        strip.show()
        time.sleep(speed)

# 메시지 스크롤 실행
scroll_message("HELLO")
