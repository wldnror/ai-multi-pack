import cv2
import numpy as np

# YOLO 모델 불러오기
net = cv2.dnn.readNet('/home/user/LED/black_box/yolov4.weights', '/home/user/LED/black_box/yolov4.cfg')

# 클래스 이름 불러오기
classes = []
with open("/home/user/LED/black_box/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
# getUnconnectedOutLayers()의 출력을 적절하게 처리
out_layer_indices = net.getUnconnectedOutLayers()
if out_layer_indices.ndim == 1:  # 최신 OpenCV 버전에서는 1D 배열로 반환
    output_layers = [layer_names[i - 1] for i in out_layer_indices.flatten()]
else:  # 이전 OpenCV 버전에서는 2D 배열로 반환
    output_layers = [layer_names[i[0] - 1] for i in out_layer_indices]

# 카메라 캡처 시작
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    height, width, channels = frame.shape

    # 객체 탐지 수행
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # 정보를 화면에 표시
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # 객체 탐지
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # 사각형 좌표
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            if label == "person" or label == "car":
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y + 30), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
    
    # 결과 화면에 표시
    cv2.imshow("Image", frame)
    key = cv2.waitKey(1)
    if key == 27:  # ESC 키
        break

cap.release()
cv2.destroyAllWindows()
