import cv2

cap = cv2.VideoCapture(0)  # 웹캠 열기

# 해상도를 1920x1080으로 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 설정한 해상도를 확인
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print("Set resolution: {}x{}".format(width, height))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)  # 실제 카메라의 FPS를 얻음
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))  # 실제 FPS 및 설정한 해상도 사용

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 프레임 처리 로직 (예: 객체 탐지)

    out.write(frame)  # 처리된 프레임을 출력 파일에 기록
    
    cv2.imshow('Frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
