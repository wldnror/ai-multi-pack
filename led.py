# TEST1

# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# # LED 매트릭스 설정
# options = RGBMatrixOptions()
# options.rows = 16  # 패널의 행 수
# options.cols = 16  # 패널의 열 수
# options.chain_length = 4  # 연결된 패널 수
# options.parallel = 1  # 병렬로 연결된 패널 수
# options.hardware_mapping = 'regular'  # 하드웨어에 맞게 설정

# # RGB 매트릭스 객체 생성
# matrix = RGBMatrix(options=options)

# # 그래픽스 도구 생성
# canvas = matrix.CreateFrameCanvas()
# font = graphics.Font()
# font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf")
# textColor = graphics.Color(255, 255, 255)
# pos = canvas.width

# # 중앙에 원을 그립니다.
# center_x = canvas.width // 2
# center_y = canvas.height // 2
# radius = min(center_x, center_y) - 2  # 패널 크기에 맞게 반지름 설정
# color = graphics.Color(255, 0, 0)  # 빨간색으로 설정

# # 캔버스를 검은색으로 초기화
# canvas.Clear()

# # 원 그리기
# graphics.DrawCircle(canvas, center_x, center_y, radius, color)
# # 변경사항을 LED 매트릭스에 적용
# canvas = matrix.SwapOnVSync(canvas)

# try:
#     print("Press CTRL-C to stop.")
#     while True:
#         # 실행을 유지합니다. CTRL-C를 누르면 종료됩니다.
#         pass
# except KeyboardInterrupt:
#     # 프로그램 종료 전에 LED 매트릭스를 깨끗하게 지웁니다.
#     canvas.Clear()
#     matrix.Clear()

# # TEST2

# import board
# import neopixel
# import time

# # 사용할 GPIO 핀 설정 (라즈베리 파이 제로의 경우 GPIO 18)
# pixel_pin = board.D18

# # LED의 개수 설정
# num_pixels = 288

# # NeoPixel 객체 생성
# pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

# # LED 스트립에 색상을 설정하는 함수
# def color_chase(color, wait):
#     for i in range(num_pixels):
#         pixels[i] = color
#         time.sleep(wait)
#         pixels.show()
#     time.sleep(0.01)

# # 색상을 RGB 값으로 정의
# RED = (255, 0, 0)
# GREEN = (0, 255, 0)
# BLUE = (0, 0, 255)

# # 메인 함수
# def main():
#     while True:
#         # 빨간색을 쫓아가는 효과
#         color_chase(RED, 0.01)
#         # 초록색을 쫓아가는 효과
#         color_chase(GREEN, 0.01)
#         # 파란색을 쫓아가는 효과
#         color_chase(BLUE, 0.01)

# # 메인 함수 실행
# if __name__ == "__main__":
#     main()

# # TEST3
# # 두 개의 144 LED 네오픽셀 패널을 제어하는 코드 예시입니다.
# # 이 코드는 각 패널에 대해 간단한 애니메이션을 실행합니다.

# import board
# import neopixel
# import time

# # 사용할 GPIO 핀 설정 (라즈베리 파이 제로의 경우 GPIO 18)
# pixel_pin = board.D18

# # 각 패널의 LED 개수 설정
# num_pixels_per_panel = 144
# total_pixels = num_pixels_per_panel * 2  # 총 LED 개수

# # NeoPixel 객체 생성
# pixels = neopixel.NeoPixel(pixel_pin, total_pixels, brightness=0.2, auto_write=False)

# # 패널에 색상을 채우는 함수
# def fill_panel(panel_num, color):
#     start_index = panel_num * num_pixels_per_panel
#     end_index = start_index + num_pixels_per_panel
#     for i in range(start_index, end_index):
#         pixels[i] = color
#     pixels.show()

# # 메인 함수
# def main():
#     while True:
#         # 첫 번째 패널을 빨간색으로 채움
#         fill_panel(0, (255, 0, 0))
#         time.sleep(1)
#         # 첫 번째 패널을 꺼짐
#         fill_panel(0, (0, 0, 0))
        
#         # 두 번째 패널을 파란색으로 채움
#         fill_panel(1, (0, 0, 255))
#         time.sleep(1)
#         # 두 번째 패널을 꺼짐
#         fill_panel(1, (0, 0, 0))

# # 메인 함수 실행
# if __name__ == "__main__":
#     main()


# 수정된 코드: 100번째부터 200번째 LED까지만 파란색으로 점등하는 예시

import board
import neopixel
import time

# 사용할 GPIO 핀 설정 (GPIO 18)
pixel_pin = board.D18

# LED의 총 개수 설정
num_pixels = 288

# NeoPixel 객체 생성
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB)

# 특정 범위의 LED에 색상을 적용하는 함수
def color_wipe(start_pixel, end_pixel, color, wait):
    # 모든 LED를 끕니다 (초기화).
    pixels.fill((0, 0, 0))
    pixels.show()

    # 지정된 범위의 LED에만 색을 적용합니다.
    for i in range(start_pixel, end_pixel):
        pixels[i] = color
        pixels.show()
        time.sleep(wait)

# 색상 정의
BLUE = (0, 0, 255)

# 메인 함수
def main():
    # 100번째부터 200번째 LED까지만 파란색으로 켜는 효과를 반복합니다.
    while True:
        color_wipe(99, 200, BLUE, 0.01)  # 100번째 LED는 인덱스 99로 시작합니다.

# 메인 함수 실행
if __name__ == "__main__":
    main()
