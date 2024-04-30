import smbus2
import time
import RPi.GPIO as GPIO

# GPIO 설정
left_led_pin = 17  # 좌회전 LED
right_led_pin = 27 # 우회전 LED
GPIO.setmode(GPIO.BCM)
GPIO.setup(left_led_pin, GPIO.OUT)
GPIO.setup(right_led_pin, GPIO.OUT)

# MPU-6050 설정
power_mgmt_1 = 0x6b
device_address = 0x68  # MPU-6050의 기본 I2C 주소
bus = smbus2.SMBus(1)

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

# 히스테리시스 적용 상태
emergency_active = False

def check_emergency_hysteresis(accel_x, gyro_z, accel_threshold, gyro_threshold, offset):
    global emergency_active
    if abs(accel_x) < accel_threshold + offset and abs(gyro_z) < gyro_threshold + offset:
        emergency_active = True
    elif abs(accel_x) > accel_threshold + offset or abs(gyro_z) > gyro_threshold + offset:
        emergency_active = False

def blink_led(pin, active):
    if active:
        GPIO.output(pin, True)
        time.sleep(0.5)  # LED가 켜져 있는 시간
        GPIO.output(pin, False)
        time.sleep(0.5)  # LED가 꺼져 있는 시간
    else:
        GPIO.output(pin, False)

def main():
    init_MPU6050()
    try:
        while True:
            accel_x = read_sensor_data(0x3b)
            gyro_z = read_sensor_data(0x47)

            # 비상등 히스테리시스 적용
            check_emergency_hysteresis(accel_x, gyro_z, 500, 100, 50)

            if emergency_active:
                blink_led(left_led_pin, True)
                blink_led(right_led_pin, True)
            else:
                blink_led(left_led_pin, left_active)
                blink_led(right_led_pin, right_active)

    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
