import cv2

def detect_and_overlay(main_cam, detection_cam):
    main_cap = cv2.VideoCapture(main_cam)
    detect_cap = cv2.VideoCapture(detection_cam)

    while True:
        ret_main, frame_main = main_cap.read()
        ret_detect, frame_detect = detect_cap.read()

        if not ret_main or not ret_detect:
            print("Error: 카메라에서 비디오를 캡처할 수 없습니다.")
            break

        # 감지 로직 (여기서는 단순화를 위해 예시로 표시)
        # 예를 들어, 움직임 감지 등의 로직을 여기에 구현합니다.
        
        # 메인 프레임에 결과 오버레이 (예시)
        # 실제 구현에는 감지 결과에 따라 조건문과 오버레이 로직이 포함될 수 있습니다.
        frame_main[10:50, 10:50] = frame_detect[10:50, 10:50]  # 간단한 예시: 일부 영역을 복사

        # 결과 표시
        cv2.imshow('Main Stream with Overlay', frame_main)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    main_cap.release()
    detect_cap.release()
    cv2.destroyAllWindows()

# 메인 카메라와 감지 카메라를 설정
detect_and_overlay('/dev/video0', '/dev/video2')
