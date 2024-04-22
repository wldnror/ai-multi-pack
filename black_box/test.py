import cv2
import numpy as np
import matplotlib.pyplot as plt

# YOLO 모델 불러오기
net = cv2.dnn.readNet('/home/user/LED/black_box/yolov4.weights', '/home/user/LED/black_box/yolov4.cfg')

# 클래스 이름 불러오기
classes = []
with open("/home/user/LED/black_box/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

plt.ion()  # 대화형 모드 활성화

fig, ax = plt.subplots()
while True:
    _, frame = cap.read()
    height, width, channels = frame.shape

    # 객체 탐지를 위한 전처리
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # 감지된 객체 정보 저장
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # 겹치는 박스 제거
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    for i in indexes:
        i = i[0]
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        color = (0, 255, 0)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Matplotlib으로 결과 표시
    ax.clear()
    ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.pause(0.01)

    if plt.waitforbuttonpress(0.01):
        break

cap.release()
cv2.destroyAllWindows()
plt.close()
