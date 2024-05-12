import smbus2
import time
import RPi.GPIO as GPIO
import argparse
import math

# GPIO 설정
left_led_pin = 17  # 좌회전 LED
right_led_pin = 26 # 우회전 LED
GPIO.setmode(GPIO.BCM)
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
    GPIO.output(pin, active)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", help="Enable manual mode", action="store_true")
    parser.add_argument("--left_on", help="Turn on the left LED", action="store_true")
    parser.add_argument("--left_off", help="Turn off the left LED", action="store_true")
    parser.add_argument("--right_on", help="Turn on the right LED", action="store_true")
    parser.add_argument("--right_off", help="Turn off the right LED", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    global manual_mode, left_active, right_active

    if args.manual:
        manual_mode = True
        if args.left_on:
            left_active = True
        elif args.left_off:
            left_active = False
        if args.right_on:
            right_active = True
        elif args.right_off:
            right_active = False

    init_MPU6050()
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

            blink_led(left_led_pin, left_active)
            blink_led(right_led_pin, right_active)
            time.sleep(0.1)
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
