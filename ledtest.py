import RPi.GPIO as GPIO
import time

# LED가 연결된 GPIO 핀 번호
LED_PIN = 18

# GPIO 핀 번호 할당 방식 설정
GPIO.setmode(GPIO.BCM)

# LED 핀을 출력으로 설정
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    # 무한 반복하여 LED를 켜고 끕니다.
    while True:
        print("LED 켜기")
        GPIO.output(LED_PIN, GPIO.HIGH)  # LED를 켭니다.
        time.sleep(1)  # 1초 동안 대기

        print("LED 끄기")
        GPIO.output(LED_PIN, GPIO.LOW)  # LED를 끕니다.
        time.sleep(1)  # 1초 동안 대기

# 사용자가 Ctrl+C를 눌러 프로그램을 종료할 때까지 계속 실행합니다.
except KeyboardInterrupt:
    # GPIO 설정 초기화
    GPIO.cleanup()
