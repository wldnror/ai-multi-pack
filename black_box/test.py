import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 웹캠 설정
cap = cv2.VideoCapture(0)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 녹화 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output11.mp4', fourcc, 30.0, (width, height))

# 폰트 설정
fontpath = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # 라즈베리 파이에서 사용 가능한 폰트 경로
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

    # Pillow 이미지로 변환
    img_pil = Image.fromarray(frame)
    draw = ImageDraw.Draw(img_pil)

    # results.xyxy[0]은 탐지된 객체들의 정보를 포함하는 텐서
    for det in results.xyxy[0]:
        x1, y1, x2, y2, conf, cls = int(det[0]), int(det[1]), int(det[2]), int(det[3]), det[4], int(det[5])
        if cls == 0:  # 'person' 클래스의 ID
            label = "사람"
        elif cls == 2:  # 'car' 클래스의 ID
            label = "자동차"
        else:
            continue  # 다른 객체는 무시

        # 레이블 및 바운딩 박스 출력 (Pillow 사용)
        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=2)
        draw.text((x1, y1 - 30), f'{label} {conf:.2f}', font=font, fill=(255, 255, 255))

    # NumPy 배열로 변환
    frame = np.array(img_pil)

    cv2.imshow('YOLOv5 Detection', frame)
    out.write(frame)

    if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() > record_time:
        break

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
