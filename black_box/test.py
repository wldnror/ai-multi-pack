import os
import time
import cv2
import configparser
from ftplib import FTP
import psutil  # 시스템 모니터링을 위한 라이브러리
import threading
import queue

# 설정 파일에서 FTP 정보를 읽어옴
def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

def init_ftp_config():
    config = configparser.ConfigParser()
    config['FTP'] = {
        'ftp_address': input('FTP 주소 입력: '),
        'ftp_username': input('FTP 사용자 이름 입력: '),
        'ftp_password': input('FTP 비밀번호 입력: '),
        'ftp_target_path': input('FTP 대상 경로 입력: ')
    }
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    with open(config_file_path, 'w') as configfile:
        config.write(configfile)

def check_config_exists():
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP 설정 파일이 없습니다. 설정을 시작합니다.")
        init_ftp_config()
    else:
        print("기존의 FTP 설정을 불러옵니다.")

class MockSMBus:
    def __init__(self, bus_number):
        self.value = 0

    def write_byte_data(self, addr, reg, value):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        return [self.value >> 8 & 0xFF, self.value & 0xFF]

    def set_acceleration(self, new_value):
        self.value = new_value

def capture_frames(cap, frame_queue, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        frame_queue.put(frame)
    frame_queue.put(None)  # Signal to stop writing frames

def write_frames(output_filename, frame_queue):
    frame = frame_queue.get()
    if frame is None:
        return  # No frames to write
    height, width = frame.shape[:2]
    fps = 30  # Assuming the fps is constant
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))
    while frame is not None:
        out.write(frame)
        frame = frame_queue.get()
    out.release()

def start_recording(duration=30):
    cap = cv2.VideoCapture(camera_device_id, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Camera could not be opened.")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)

    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')

    frame_queue = queue.Queue(10)
    capture_thread = threading.Thread(target=capture_frames, args=(cap, frame_queue, duration))
    write_thread = threading.Thread(target=write_frames, args=(output_filename, frame_queue))

    capture_thread.start()
    write_thread.start()

    capture_thread.join()
    write_thread.join()

    cap.release()
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

camera_device_id = 0
bus = MockSMBus(1)
device_address = 0x68
bus.write_byte_data(device_address, 0x6B, 0)

def read_acceleration(axis):
    data = bus.read_i2c_block_data(device_address, axis, 2)
    value = data[0] << 8 | data[1]
    if value > 32767:
        value -= 65536
    return value

threshold = 15000
check_config_exists()
try:
    while True:
        input_value = int(input("가속도 값 입력 (0-65535): "))
        bus.set_acceleration(input_value)
        acceleration = read_acceleration(0x3B)
        if abs(acceleration) > threshold:
            print("충격 감지! 녹화 시작")
            output_file = start_recording(30)
            if output_file:
                upload_file_to_ftp(output_file)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("테스트 종료.")
