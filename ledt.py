import time
import board
import neopixel
import smbus

# MPU-6050 설정
power_mgmt_1 = 0x6b
bus = smbus.SMBus(1)
address = 0x68  # MPU-6050의 기본 I2C 주소

# NeoPixel LED 설정
pixel_pin = board.D18
num_pixels_per_panel = 144
total_pixels = num_pixels_per_panel * 2
pixels = neopixel.NeoPixel(pixel_pin, total_pixels, brightness=0.2, auto_write=False)

def init_mpu6050():
    bus.write_byte_data(address, power_mgmt_1, 0)

def read_accelerometer(axis):
    high = bus.read_byte_data(address, axis)
    low = bus.read_byte_data(address, axis + 1)
    value = (high << 8) + low
    if value >= 0x8000:
        return -((65535 - value) + 1)
    else:
        return value

def fill_panel(panel_num, color):
    start_index = panel_num * num_pixels_per_panel
    end_index = start_index + num_pixels_per_panel
    for i in range(start_index, end_index):
        pixels[i] = color
    pixels.show()

def control_leds():
    init_mpu6050()
    while True:
        accel_x = read_accelerometer(0x3b)  # X축 가속도 값 읽기
        print(f"Current X-axis acceleration: {accel_x}")  # 현재 X축 가속도 값 출력

        if accel_x > 1500:
            # 우측 기울기: 첫 번째 패널 (빨간색) 활성화
            fill_panel(0, (255, 0, 0))
            fill_panel(1, (0, 0, 0))
        elif accel_x < -1500:
            # 좌측 기울기: 두 번째 패널 (파란색) 활성화
            fill_panel(0, (0, 0, 0))
            fill_panel(1, (0, 0, 255))
        else:
            # 기울기 없음: 모든 패널 비활성화
            fill_panel(0, (0, 0, 0))
            fill_panel(1, (0, 0, 0))

        time.sleep(0.3)

if __name__ == "__main__":
    control_leds()
