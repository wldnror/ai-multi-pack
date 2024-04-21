import cv2  # cv2 모듈을 불러옵니다.

# 비디오 캡처 객체를 생성합니다. 여기서 '0'은 시스템의 기본 카메라를 의미합니다.
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# cap 객체의 초기화 상태를 확인합니다.
if cap.isOpened():
    print("카메라가 성공적으로 열렸습니다.")
    # 지원하는 해상도 및 프레임 레이트를 출력합니다.
    print("Width: ", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print("Height: ", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("FPS: ", cap.get(cv2.CAP_PROP_FPS))
else:
    print("카메라를 열 수 없습니다.")

# 비디오 캡처 객체를 해제합니다.
cap.release()
