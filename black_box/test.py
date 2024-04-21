import os
import time
import cv2
from ftplib import FTP
import configparser
import psutil  # 시스템 모니터링을 위한 라이브러리 추가

# 설정 파일에서 FTP 정보를 읽어옴
def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

# FTP 서버 정보 설정
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
        self.value = 0  # 초기 가속도 값은 0

    def write_byte_data(self, addr, reg, value):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        # 현재 설정된 가속도 값 반환
        return [self.value >> 8 & 0xFF, self.value & 0xFF]

    def set_acceleration(self, new_value):
        self.value = new_value  # 새로운 가속도 값 설정

camera_device_id = 0  # Logitech BRIO 장치 ID를 0으로 가정합니다.

def start_recording(duration=30):
    cap = cv2.VideoCapture(camera_device_id, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("카메라를 시작할 수 없습니다.")
        return None

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 30)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    frame_count = 0
    start_time = time.time()
    while (time.time() - start_time) < duration:
        cpu_usage = psutil.cpu_percent(interval=None)  # CPU 사용량 측정
        memory_usage = psutil.virtual_memory().percent  # 메모리 사용량 측정

        ret, frame = cap.read()
        if ret:
            frame_start = time.time()
            out.write(frame)
            frame_duration = time.time() - frame_start
            print(f"Frame {frame_count}: {frame_duration:.5f} seconds - CPU {cpu_usage}%, Memory {memory_usage}%")
            frame_count += 1
        else:
            break

    print(f"Recorded {frame_count} frames in {time.time() - start_time:.2f} seconds at {fps} FPS.")

    cap.release()
    out.release()
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

bus = MockSMBus(1)
device_address = 0x68
bus.write_byte_data(device_address, 0x6B, 0)

def read_acceleration(axis):
    data = bus.read_i2c_block_data(device_address, axis, 2)
    value = data[0] << 8 | data[1]
    if value > 32767:
        value -= 65536
    return value

threshold = 15000  # 임계값 설정
check_config_exists()  # 프로그램 시작 시 설정 파일 확인
try:
    while True:
        # 사용자 입력을 받아 충격 감지 여부 결정
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
