import board
import neopixel
import time

# 매트릭스 LED 설정
LED_COUNT = 288      # LED 개수
LED_PIN = board.D21   # GPIO 핀 번호
LED_BRIGHTNESS = 0.5 # LED 밝기 (0.0에서 1.0 사이)

# NeoPixel 객체 초기화
strip = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# 모든 LED를 빨간색으로 켜고 1초 동안 대기
strip.fill((255, 0, 0))
strip.show()
time.sleep(1)

# 모든 LED를 녹색으로 켜고 1초 동안 대기
strip.fill((0, 255, 0))
strip.show()
time.sleep(1)

# 모든 LED를 파란색으로 켜고 1초 동안 대기
strip.fill((0, 0, 255))
strip.show()
time.sleep(1)

# 모든 LED를 꺼고 1초 동안 대기
strip.fill((0, 0, 0))
strip.show()
time.sleep(1)
