import os
import time
import configparser
import cv2
import torch
from ftplib import FTP

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def check_config_exists():
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP 설정 파일이 없습니다. 설정을 시작합니다.")
        init_ftp_config()
    else:
        print("기존의 FTP 설정을 불러옵니다.")

def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

def start_detection_and_recording(duration=10):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    os.makedirs(output_directory, exist_ok=True)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.avi')
    out = cv2.VideoWriter(output_filename, fourcc, 1.58, (1920, 1080))

    frame_count = 0
    start_time = time.time()

    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        for det in results.xyxy[0]:
            x1, y1, x2, y2, conf, cls = map(int, det[:6])
            if cls in [0, 2]:
                label = "사람" if cls == 0 else "자동차"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        out.write(frame)
        frame_count += 1

    elapsed_time = time.time() - start_time
    actual_fps = frame_count / elapsed_time
    print(f"Recorded {frame_count} frames in {elapsed_time:.2f} seconds, actual FPS: {actual_fps:.2f}")

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return output_filename

def upload_file_to_ftp(file_path):
    try:
        ftp_info = read_ftp_config()
        ftp = FTP(ftp_info['ftp_address'])
        ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
        with open(file_path, 'rb') as file:
            ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}/{os.path.basename(file_path)}", file)
        print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")
    finally:
        ftp.quit()

# 메인 루프
check_config_exists()
try:
    while True:
        input_value = int(input("가속도 값 입력 (0-65535): "))
        if input_value > 15000:
            print("충격 감지! 녹화 시작")
            output_file = start_detection_and_recording(30)
            if output_file:
                upload_file_to_ftp(output_file)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("테스트 종료.")
