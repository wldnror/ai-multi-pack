import cv2

cap = cv2.VideoCapture(0)  # 웹캠 열기

# 실제 카메라에서 사용되는 프레임 레이트를 얻습니다.
fps = cap.get(cv2.CAP_PROP_FPS)

# 비디오 스트림의 너비와 높이를 가져옵니다.
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))  # 실제 FPS 및 해상도 사용

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
