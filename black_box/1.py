import cv2
import time

print("Starting the program...")

# 카메라 열기
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Camera could not be opened.")
else:
    print("Camera opened successfully.")

# 해상도 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 설정한 해상도 확인
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"Set resolution: {width}x{height}")

# 비디오 라이터 설정
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, 30.0, (width, height))
print("VideoWriter initialized.")

# 프레임 레이트 계산을 위한 변수
frame_count = 0
start_time = time.time()

# 비디오 녹화
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("No frame read from camera.")
            break

        frame_count += 1
        out.write(frame)  # 프레임을 비디오 파일에 저장
        cv2.imshow('Frame', frame)  # 화면에 프레임 표시

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting loop by user command.")
            break
except Exception as e:
    print(f"An error occurred: {e}")

elapsed_time = time.time() - start_time
actual_fps = frame_count / elapsed_time
print(f"Actual FPS: {actual_fps}")

# 자원 정리
cap.release()
out.release()
cv2.destroyAllWindows()
print("Resources released, program ended.")
