import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 카메라 설정
cap = cv2.VideoCapture('/dev/video0')  # 카메라 디바이스 지정
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 녹화 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output11.mp4', fourcc, 30.0, (width, height))

# 폰트 설정 (라즈베리파이에 맞는 폰트 파일 경로 설정 필요)
fontpath = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"  # 폰트 파일 경로
font = ImageFont.truetype(fontpath, 20)

# 녹화 시간 계산을 위한 변수
start_time = cv2.getTickCount()
record_time = 10  # 녹화 시간 (초)

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
        draw.text((x1, y1 -30)로 지정한 후 (x1, y1 - 30) 위치에 텍스트를 그립니다. 텍스트에는 레이블과 신뢰도(confidence)를 표시합니다.

    # NumPy 배열로 다시 변환하여 OpenCV에서 처리 가능하도록 함
    frame = np.array(img_pil)

    # 결과 화면에 표시
    cv2.imshow('YOLOv5 Detection', frame)
    out.write(frame)  # 프레임을 파일로 저장

    # 설정한 녹화 시간이 경과했는지 확인
    if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() > record_time:
        break

    # 'q' 키를 누르면 루프 탈출
    if cv2.waitKey(1) == ord('q'):
        break

# 자원 해제
cap.release()
out.release()
cv2.destroyAllWindows()
