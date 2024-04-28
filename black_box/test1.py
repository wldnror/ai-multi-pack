import cv2

def detect_objects_and_overlay(main_cam, detection_cam):
    main_cap = cv2.VideoCapture(main_cam)
    detect_cap = cv2.VideoCapture(detection_cam)

    # 객체 감지를 위한 준비 (여기서는 얼굴 인식 예제 사용)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    while True:
        ret_main, frame_main = main_cap.read()
        ret_detect, frame_detect = detect_cap.read()

        if not ret_main or not ret_detect:
            print("Error: 카메라에서 비디오를 캡처할 수 없습니다.")
            break

        # 감지 로직
        gray = cv2.cvtColor(frame_detect, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # 감지된 객체에 사각형 그리기
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_detect, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # 메인 프레임에 감지 결과 오버레이
        frame_main[0:frame_detect.shape[0], 0:frame_detect.shape[1]] = frame_detect

        # 결과 표시
        cv2.imshow('Main Stream with Overlay', frame_main)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    main_cap.release()
    detect_cap.release()
    cv2.destroyAllWindows()

# 메인 카메라와 감지 카메라를 설정
detect_objects_and_overlay('/dev/video0', '/dev/video2')
