import RPi.GPIO as GPIO

green_led_pin = 11  # 초록색 LED 핀 (BCM 11, 물리적 핀 23)

GPIO.setmode(GPIO.BCM)
GPIO.setup(green_led_pin, GPIO.OUT)

# 초록색 LED를 켜기
GPIO.output(green_led_pin, GPIO.HIGH)

# 10초 동안 대기
try:
    input("초록색 LED가 켜졌는지 확인하세요. 계속하려면 Enter 키를 누르세요...")
except KeyboardInterrupt:
    pass

# GPIO 설정 초기화
GPIO.cleanup()
