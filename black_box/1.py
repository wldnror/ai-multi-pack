if cap.isOpened():
    # 지원하는 해상도 및 프레임레이트 출력
    print("Width: ", cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print("Height: ", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("FPS: ", cap.get(cv2.CAP_PROP_FPS))
cap.release()
