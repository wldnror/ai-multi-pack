import smbus2
import time
import RPi.GPIO as GPIO
import argparse
import socket
import subprocess
import math
import sys
import json
import bluetooth
from rpi_ws281x import PixelStrip, Color
import pygame  # Pygame 모듈 추가

# GPIO 설정
left_led_pin = 17  # 좌회전 LED
right_led_pin = 18 # 우회전 LED
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # GPIO 경고 비활성화

# 네오픽셀 설정
LED_COUNT = 16  # LED 개수
LED_PIN = 21  # GPIO 핀
LED_FREQ_HZ = 800000  # LED 신호 주파수
LED_DMA = 10  # DMA 채널
LED_BRIGHTNESS = 255  # 밝기 (0-255)
LED_INVERT = False  # 신호 반전 여부
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# MPU-6050 설정
power_mgmt_1 = 0x6b
device_address = 0x69  # MPU-6050의 기본 I2C 주소
bus = smbus2.SMBus(1)

# UDP 소켓 설정
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broadcast_ip = '255.255.255.255'  # 브로드캐스트 IP
udp_port = 5005  # UDP 포트

# 전역 변수 설정
manual_mode = False
left_active = False
right_active = False

# Pygame 초기화
pygame.mixer.init()

def get_ip_address():
    return subprocess.check_output(["hostname", "-I"]).decode().strip().split()[0]

def init_GPIO():
    GPIO.cleanup()  # 기존 설정 클린업
    GPIO.setmode(GPIO.BCM)  # GPIO 모드 재설정
    GPIO.setup(left_led_pin, GPIO.OUT)
    GPIO.setup(right_led_pin, GPIO.OUT)
    print("GPIO 초기화 완료")

# MPU-6050 초기화
def init_MPU6050():
    bus.write_byte_data(device_address, power_mgmt_1, 0)
    print("MPU-6050 초기화 완료")

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

def send_udp_message(pin, state):
    mode_status = "manual" if manual_mode else "auto"
    full_message = {
        "mode": mode_status,
        "message": {"pin": pin, "state": state}
    }
    print(f"Sending UDP message: {full_message}")
    sock.sendto(json.dumps(full_message).encode(), (broadcast_ip, udp_port))

def blink_led(pin, active):
    GPIO.output(pin, active)
    state = "ON" if active else "OFF"
    send_udp_message(pin, state)
    time.sleep(0.4)
    GPIO.output(pin, not active)
    state = "OFF" if active else "ON"
    send_udp_message(pin, state)
    time.sleep(0.4)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual", help="Enable manual mode", action="store_true")
    parser.add_argument("--left", "--left_on", help="Turn on the left LED", action="store_true", dest='left')
    parser.add_argument("--right", "--right_on", help="Turn on the right LED", action="store_true", dest='right')
    parser.add_argument("--auto", help="Enable automatic mode", action="store_true")
    return parser.parse_args()

def is_bluetooth_connected():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
    return len(nearby_devices) > 0

def rainbow_cycle(wait):
    for j in range(256):
        for i in range(strip.numPixels()):
            pixel_index = (i * 256 // strip.numPixels()) + j
            strip.setPixelColor(i, wheel(pixel_index & 255))
        strip.show()
        time.sleep(wait)

def wheel(pos):
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def is_sound_playing():
    return pygame.mixer.get_busy()

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
            if not is_bluetooth_connected():
                print("블루투스 연결이 필요합니다.")
                time.sleep(5)
                continue

            if not is_sound_playing():
                rainbow_cycle(0.01)
                continue

            if not manual_mode:
                accel_x = read_sensor_data(0x3b)
                accel_y = read_sensor_data(0x3d)
                accel_z = read_sensor_data(0x3f)
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

            if left_active:
                GPIO.output(right_led_pin, False)  # 오른쪽 LED 끄기
                blink_led(left_led_pin, True)
            elif right_active:
                GPIO.output(left_led_pin, False)  # 왼쪽 LED 끄기
                blink_led(right_led_pin, True)

            time.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

if __name__ == '__main__':
    main()
