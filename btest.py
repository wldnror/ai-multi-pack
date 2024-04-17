import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# 모델 파일 로드
model_path = '/home/user/yolov5/yolov5s.pt', 'yolov5s', pretrained=True)  # 예시 모델 경로

# 카메라 설정
cap = cv2.VideoCapture('/dev/video0')  # Logitech BRIO assumed to be at /dev/video0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 녹화 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output11.mp4', fourcc, 30.0, (width, height))

# 폰트 설정 (라즈베리파이에 적절한 폰트 파일 경로 설정)
fontpath = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
font = ImageFont.truetype(fontpath, 20)

# 녹화 시간 계산을 위한 변수
start_time = cv2.getTickCount()
record_time = 10

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv5로 추론
    results = model(frame)

    # Pillow 이미지로 변환하여 텍스트 그리기
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    # results.xyxy[0]은 탐지된 객체들의 정보를 포함하는 텐서
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = int(det[0]), int(det[1]), int(det[2]), int(det[3]), det[4], int(det[5])
        if cls == 0:  # 'person' 클래스 ID
            label = "사람"
        elif cls == 2:  # 'car' 클래스 ID
            label = "자동차"
        else:
            continue  # 다른 객체는 무시

        # 레이블 및 바운딩 박스 출력
        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=2)
        draw.text((x1, y1 - 30), f'{label} {conf:.2f}', font=font, fill=(255, 255, 255))

    # NumPy 배열로 다시 변환하여 OpenCV에서 처리 가능하도록 함
    frame = np.array(img_pil)

    # 결과 화면에 표시
    cv2.imshow('YOLOv5 Detection', frame)
    out.write(frame)

    if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() > record_time:
        break

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
