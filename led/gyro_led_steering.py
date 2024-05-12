import smbus2
import time
import RPi.GPIO as GPIO
import argparse
import math
import sys

# GPIO 설정
left_led_pin = 17  # 좌회전 LED
right_led_pin = 26 # 우회전 LED
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # GPIO 경고 비활성화
GPIO.setup(left_led_pin, GPIO.OUT)
GPIO.setup(right_led_pin, GPIO.OUT)

# MPU-6050 설정
power_mgmt_1 = 0x6b
device_address = 0x68  # MPU-6050의 기본 I2C 주소
bus = smbus2.SMBus(1)

# 전역 변수 설정
manual_mode = False
left_active = False
right_active = False

def init_GPIO():
    GPIO.cleanup()  # 기존 설정 클린업
    GPIO.setmode(GPIO.BCM)  # GPIO 모드 재설정
    GPIO.setup(left_led_pin, GPIO.OUT)
    GPIO.setup(right_led_pin, GPIO.OUT)

# MPU-6050 초기화
def init_MPU6050():
    bus.write_byte_data(device_address, power_mgmt_1, 0)

# 센서 데이터 읽기
def read_sensor_data(addr):
    high = bus.read_byte_data(device_address, addr)
    low = bus.read_byte_data(device_address, addr + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

def calculate_angle(acc_x, acc_y, acc_z):
    angle_x = math.atan2(acc_x, math.sqrt(acc_y**2 + acc_z**2)) * 180 / math.pi
    angle_y = math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2)) * 180 / math.pi
    return angle_x, angle_y

def blink_led(pin, active):
    if active:
        GPIO.output(pin, True)
        time.sleep(0.4)  # LED가 켜져 있는 시간
        GPIO.output(pin, False)
        time.sleep(0.4)  # LED가 꺼져 있는 시간
    else:
        GPIO.output(pin, False)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", help="Enable manual mode", action="store_true")
    parser.add_argument("--left", help="Turn on the left LED", action="store_true")
    parser.add_argument("--right", help="Turn on the right LED", action="store_true")
    parser.add_argument("--auto", help="Enable automatic mode", action="store_true")
    return parser.parse_args()

def main():
    global manual_mode, left_active, right_active
    args = parse_args()

    if args.manual:
        manual_mode = True
        left_active = args.left
        right_active = args.right
    elif args.auto:
        manual_mode = False
        init_MPU6050()

    init_GPIO()

    try:
        while True:
            if not manual_mode:
                accel_x = read_sensor_data(0x3b)
                accel_y = read_sensor_data(0x3d)
                accel_z = read_sensor_data(0x3f)
                gyro_y = read_sensor_data(0x45)
                _, angle_y = calculate_angle(accel_x, accel_y, accel_z)

                if angle_y > 20:
                    right_active = True
                    left_active = False
                elif angle_y < -20:
                    right_active = False
                    left_active = True
                else:
                    right_active = False
                    left_active = False
            else:
                # 수동 모드에서는 외부 명령에 의해서만 LED 상태가 변경되므로
                # 추가적인 로직 없이 대기
                time.sleep(0.1)

            blink_led(left_led_pin, left_active)
            blink_led(right_led_pin, right_active)

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

if __name__ == '__main__':
    main()
