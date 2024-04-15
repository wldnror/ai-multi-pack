# import time
# import board
# import neopixel
# import smbus

# # MPU-6050 설정
# power_mgmt_1 = 0x6b
# bus = smbus.SMBus(1)
# address = 0x68  # MPU-6050의 기본 I2C 주소

# # NeoPixel LED 설정
# pixel_pin = board.D18
# num_pixels_per_panel = 144
# total_pixels = num_pixels_per_panel * 2
# pixels = neopixel.NeoPixel(pixel_pin, total_pixels, brightness=0.2, auto_write=False)

# def init_mpu6050():
#     bus.write_byte_data(address, power_mgmt_1, 0)

# def read_accelerometer(axis):
#     high = bus.read_byte_data(address, axis)
#     low = bus.read_byte_data(address, axis + 1)
#     value = (high << 8) + low
#     if value >= 0x8000:
#         return -((65535 - value) + 1)
#     else:
#         return value

# def fill_panel(panel_num, color):
#     start_index = panel_num * num_pixels_per_panel
#     end_index = start_index + num_pixels_per_panel
#     for i in range(start_index, end_index):
#         pixels[i] = color
#     pixels.show()

# def control_leds():
#     init_mpu6050()
#     while True:
#         accel_x = read_accelerometer(0x3b)  # X축 가속도 값 읽기
#         print(f"Current X-axis acceleration: {accel_x}")  # 현재 X축 가속도 값 출력

#         if accel_x > 1500:
#             # 우측 기울기: 첫 번째 패널 (빨간색) 활성화
#             fill_panel(0, (255, 0, 0))
#             fill_panel(1, (0, 0, 0))
#         elif accel_x < -1500:
#             # 좌측 기울기: 두 번째 패널 (파란색) 활성화
#             fill_panel(0, (0, 0, 0))
#             fill_panel(1, (0, 0, 255))
#         else:
#             # 기울기 없음: 모든 패널 비활성화
#             fill_panel(0, (0, 0, 0))
#             fill_panel(1, (0, 0, 0))

#         time.sleep(0.3)

# if __name__ == "__main__":
#     control_leds()


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

def clear_leds():
    for i in range(total_pixels):
        pixels[i] = (0, 0, 0)
    pixels.show()

def sweep_panel(start_index, end_index, color, reverse=False, speed=0.05):
    indices = range(start_index, end_index, 5) if not reverse else range(end_index - 1, start_index - 1, -5)
    
    for i in indices:
        clear_leds()  # 새로운 LED 애니메이션 시작 전에 모든 LED를 끕니다.
        for j in range(5):
            pixel_index = (i + j) % num_pixels_per_panel + start_index
            if 0 <= pixel_index - start_index < num_pixels_per_panel:
                pixels[pixel_index] = color
        pixels.show()
        # 각 단계마다 기울기 체크
        current_accel_x = read_accelerometer(0x3b)
        if (current_accel_x > 1500 and reverse) or (current_accel_x < -1500 and not reverse):
            break  # 기울기 변경 시 반복 중단
        time.sleep(speed)

def control_leds():
    init_mpu6050()
    last_state = None

    while True:
        accel_x = read_accelerometer(0x3b)  # X축 가속도 값 읽기
        print(f"Current X-axis acceleration: {accel_x}")  # 현재 X축 가속도 값 출력

        if accel_x > 1500 and last_state != 'right':
            # 우측 기울기: 파란색 LED 패널 활성화 및 스윕
            last_state = 'right'
            sweep_panel(num_pixels_per_panel, total_pixels, (0, 0, 255), speed=0.05)
        elif accel_x < -1500 and last_state != 'left':
            # 좌측 기울기: 빨간색 LED 패널 역방향 활성화 및 스윕
            last_state = 'left'
            sweep_panel(0, num_pixels_per_panel, (255, 0, 0), reverse=True, speed=0.05)
        elif accel_x >= -1500 and accel_x <= 1500 and last_state != 'neutral':
            # 기울기 없음: 모든 패널 비활성화 및 상태 초기화
            last_state = 'neutral'
            clear_leds()

        time.sleep(0.1)

if __name__ == "__main__":
    control_leds()
