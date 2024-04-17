import cv2
import torch

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 웹캠 설정
cap = cv2.VideoCapture(0)
# 웹캠의 실제 프레임 해상도 가져오기
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 녹화 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 코덱 설정
out = cv2.VideoWriter('output11.mp4', fourcc, 30.0, (width, height))  # 파일명, 코덱, fps, 해상도

# 녹화 시간 계산을 위한 변수
start_time = cv2.getTickCount()
record_time = 10  # 녹화 시간 (초)

while True:
    # 웹캠에서 이미지 읽기
    ret, frame = cap.read()
    if not ret:
        break

    # YOLOv5로 추론
    results = model(frame)

    # 사람(0)과 자동차(2)만 필터링
    results = results.xyxy[0]  # 바운딩 박스 좌표
    for *xyxy, conf, cls in results:
        if cls in [0, 2]:  # cls 0은 사람, 2는 자동차
            label = model.names[int(cls)]  # 클래스 이름
            cv2.rectangle(frame, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 0, 0), 2)
            cv2.putText(frame, f'{label} {conf:.2f}', (int(xyxy[0]), int(xyxy[1]-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

    # 결과 이미지 보여주기
    cv2.imshow('YOLOv5 Detection', frame)
    out.write(frame)  # 프레임 저장

    # 녹화 시간 확인 및 종료
    if (cv2.getTickCount() - start_time) / cv2.getTickFrequency() > record_time:
        break

    if cv2.waitKey(1) == ord('q'):  # 'q'를 누르면 종료
        break

# 자원 해제
cap.release()
out.release()  # 비디오 저장 종료
cv2.destroyAllWindows()
