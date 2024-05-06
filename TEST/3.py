import RPi.GPIO as GPIO
import time

# GPIO 핀 번호 설정
pin = 17
pin = 26

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)

# GPIO 핀을 출력으로 설정
GPIO.setup(pin, GPIO.OUT)

try:
    # GPIO 핀에 3.3V 전원 출력
    GPIO.output(pin, GPIO.HIGH)
    print("GPIO", pin, "is now HIGH")

    # 상태 유지를 위해 잠시 대기
    time.sleep(10)

finally:
    # 프로그램 종료 전 GPIO 설정 초기화
    GPIO.cleanup()
    print("GPIO cleaned up")
