from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# LED 매트릭스 설정
options = RGBMatrixOptions()
options.rows = 16  # 패널의 행 수
options.cols = 16  # 패널의 열 수
options.chain_length = 4  # 연결된 패널 수
options.parallel = 1  # 병렬로 연결된 패널 수
options.hardware_mapping = 'regular'  # 하드웨어에 맞게 설정

# RGB 매트릭스 객체 생성
matrix = RGBMatrix(options=options)

# 그래픽스 도구 생성
canvas = matrix.CreateFrameCanvas()
font = graphics.Font()
font.LoadFont("/home/pi/rpi-rgb-led-matrix/fonts/7x13.bdf")
textColor = graphics.Color(255, 255, 255)
pos = canvas.width

# 중앙에 원을 그립니다.
center_x = canvas.width // 2
center_y = canvas.height // 2
radius = min(center_x, center_y) - 2  # 패널 크기에 맞게 반지름 설정
color = graphics.Color(255, 0, 0)  # 빨간색으로 설정

# 캔버스를 검은색으로 초기화
canvas.Clear()

# 원 그리기
graphics.DrawCircle(canvas, center_x, center_y, radius, color)
# 변경사항을 LED 매트릭스에 적용
canvas = matrix.SwapOnVSync(canvas)

try:
    print("Press CTRL-C to stop.")
    while True:
        # 실행을 유지합니다. CTRL-C를 누르면 종료됩니다.
        pass
except KeyboardInterrupt:
    # 프로그램 종료 전에 LED 매트릭스를 깨끗하게 지웁니다.
    canvas.Clear()
    matrix.Clear()
