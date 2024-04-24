import cv2

cap = cv2.VideoCapture(0)  # 웹캠 열기
fps = cap.get(cv2.CAP_PROP_FPS)  # 실제 카메라의 FPS를 얻음

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))  # 실제 FPS 사용

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
