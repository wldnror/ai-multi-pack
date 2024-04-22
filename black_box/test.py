import cv2
import numpy as np

# YOLO 모델 및 클래스 레이블 로드
net = cv2.dnn.readNet('/home/user/LED/black_box/yolov4.weights', '/home/user/LED/black_box/yolov4.cfg')
classes = []
with open("/home/user/LED/black_box/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
out_layer_indices = net.getUnconnectedOutLayers()
if out_layer_indices.ndim == 1:
    output_layers = [layer_names[int(index) - 1] for index in out_layer_indices]
else:
    output_layers = [layer_names[index[0] - 1] for index in out_layer_indices]

# 카메라 캡처 초기화
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    height, width, channels = frame.shape

    # 객체 탐지 수행
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

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

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    if type(indexes) == tuple:
        indexes = indexes[0]

    for i in indexes:
        x, y, w, h = boxes[int(i)]
        label = str(classes[class_ids[int(i)]])
        if label == "person" or label == "car":
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # 결과 화면에 표시
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
