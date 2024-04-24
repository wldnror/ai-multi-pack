import os
import time
import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import configparser
from ftplib import FTP
import subprocess

# YOLOv5 모델 로드
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# 설정 파일에서 FTP 정보를 읽어옴
def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

def check_config_exists():
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP 설정 파일이 없습니다.")
        return False
    else:
        print("기존의 FTP 설정을 불러옵니다.")
        return True

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

def record_and_upload():
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
    out = cv2.VideoWriter(output_filename, fourcc, 30.0, (width, height))

    start_time = cv2.getTickCount()
    record_time = 10  # seconds
    while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < record_time:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        img_pil = Image.fromarray(frame)
        draw = ImageDraw.Draw(img_pil)
        for det in results.xyxy[0]:
            # Add bounding boxes and labels
            pass
        frame = np.array(img_pil)
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    if check_config_exists():
        upload_file_to_ftp(output_filename)

if __name__ == "__main__":
    try:
        while True:
            input_value = int(input("가속도 값 입력 (0-65535): "))
            if input_value > 15000:
                print("충격 감지! 녹화 시작")
                record_and_upload()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("테스트 종료.")
