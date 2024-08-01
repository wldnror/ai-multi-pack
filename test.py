import RPi.GPIO as GPIO
import time

# GPIO 핀 설정 (물리적 핀 번호 기준)
red_led_pin = 24  # 빨간색 LED 핀 (BCM 24, 물리적 핀 18)
green_led_pin = 23  # 초록색 LED 핀 (BCM 23, 물리적 핀 16)

# GPIO 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_led_pin, GPIO.OUT)
GPIO.setup(green_led_pin, GPIO.OUT)

# PWM 설정
red_led_pwm = GPIO.PWM(red_led_pin, 100)  # 빨간색 LED 핀에서 100Hz 주파수로 PWM 설정
red_led_pwm.start(0)  # 시작 시 듀티 사이클 0%

# 초록색 LED를 항상 켜기
GPIO.output(green_led_pin, GPIO.HIGH)

try:
    while True:
        # 서서히 밝아지기
        for duty_cycle in range(0, 101, 1):
            red_led_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)  # 20ms 지연

        # 서서히 어두워지기
        for duty_cycle in range(100, -1, -1):
            red_led_pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.02)  # 20ms 지연

except KeyboardInterrupt:
    pass

# GPIO 설정 초기화
red_led_pwm.stop()
GPIO.cleanup()
