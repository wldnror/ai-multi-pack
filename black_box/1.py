import cv2
import time

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (1920, 1080))

frame_count = 0
start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # 객체 탐지 및 기타 프레임 처리 로직

    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

elapsed_time = time.time() - start_time
actual_fps = frame_count / elapsed_time
print(f"Actual FPS: {actual_fps}")

cap.release()
out.release()
cv2.destroyAllWindows()
