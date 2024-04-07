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

import board
import neopixel
import time

# 사용할 GPIO 핀 설정 (GPIO 18)
pixel_pin = board.D18

# LED의 총 개수 설정
num_pixels = 288

# NeoPixel 객체 생성
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False, pixel_order=neopixel.GRB)

def create_raindrop(start_pixel, end_pixel, color, wait):
    # 한 번에 5개의 LED를 조작합니다.
    for i in range(start_pixel, end_pixel + 5):
        # 각 LED에 대해 페이드 인 효과를 적용합니다.
        for j in range(5):
            if i - j >= start_pixel and i - j < end_pixel:
                brightness = max(0, 255 - 50 * j)  # 위쪽 LED가 더 밝게
                dimmed_color = (int(color[0] * brightness / 255), int(color[1] * brightness / 255), int(color[2] * brightness / 255))
                pixels[i - j] = dimmed_color
        pixels.show()
        time.sleep(wait)

        # 마지막 LED가 지나가면 꺼줍니다.
        if i >= 5:
            pixels[i - 5] = (0, 0, 0)

# 메인 함수
def main():
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]
    color_index = 0

    while True:
        # 현재 색상으로 비 내리는 효과를 생성합니다.
        create_raindrop(99, 200, colors[color_index], 0.05)

        # 다음 색상을 선택합니다. 첫 번째 색상이 일정 구간 내려온 후 다음 색상이 시작됩니다.
        color_index = (color_index + 1) % len(colors)
        time.sleep(2)  # 다음 색상이 시작하기 전에 잠시 대기합니다.

if __name__ == "__main__":
    main()
