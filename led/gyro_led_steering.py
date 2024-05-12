import smbus2
import time
import RPi.GPIO as GPIO
import argparse
import math
import sys
import socket
import threading

# GPIO 설정
left_led_pin = 17  # 좌회전 LED
right_led_pin = 26 # 우회전 LED
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(left_led_pin, GPIO.OUT)
GPIO.setup(right_led_pin, GPIO.OUT)

# MPU-6050 설정
power_mgmt_1 = 0x6b
device_address = 0x68
bus = smbus2.SMBus(1)

# 전역 변수 설정
manual_mode = False
left_active = False
right_active = False

# UDP 서버 설정
udp_ip = "0.0.0.0"
udp_port = 12345

def init_GPIO():
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(left_led_pin, GPIO.OUT)
    GPIO.setup(right_led_pin, GPIO.OUT)

def init_MPU6050():
    bus.write_byte_data(device_address, power_mgmt_1, 0)

def read_sensor_data(addr):
    high = bus.read_byte_data(device_address, addr)
    low = bus.read_byte_data(device_address, addr + 1)
    value = (high << 8) + low
    return -((65535 - value) + 1) if value >= 0x8000 else value

def calculate_angle(acc_x, acc_y, acc_z):
    angle_y = math.atan2(acc_y, math.sqrt(acc_x**2 + acc_z**2)) * 180 / math.pi
    return angle_y

def blink_led(pin, active):
    GPIO.output(pin, active)
    time.sleep(0.4)
    GPIO.output(pin, False)
    time.sleep(0.4)

def udp_server():
    global left_active, right_active
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")
    
    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        if message == "Right Blinker Activated":
            right_active = True
            left_active = False
        elif message == "Left Blinker Activated":
            left_active = True
            right_active = False

def main():
    global manual_mode, left_active, right_active
    args = parse_args()
    manual_mode = args.manual
    left_active = args.left
    right_active = args.right

    threading.Thread(target=udp_server).start()  # UDP 서버 스레드 시작

    if not manual_mode:
        init_MPU6050()

    try:
        while True:
            if not manual_mode:
                accel_x = read_sensor_data(0x3b)
                accel_y = read_sensor_data(0x3d)
                accel_z = read_sensor_data(0x3f)
                angle_y = calculate_angle(accel_x, accel_y, accel_z)

                right_active = angle_y > 20
                left_active = angle_y < -20

            blink_led(left_led_pin, left_active)
            blink_led(right_led_pin, right_active)

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

if __name__ == '__main__':
    main()
