import os
import time
import cv2
from ftplib import FTP
import configparser

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
    if not os.path.exists('ftp_config.ini'):
        print("FTP 설정 파일이 없습니다. 설정을 시작합니다.")
        init_ftp_config()
    else:
        print("기존의 FTP 설정을 불러옵니다.")

def read_ftp_config():
    config = configparser.ConfigParser()
    config.read('ftp_config.ini')
    return config['FTP']

class MockSMBus:
    def __init__(self, bus_number):
        self.value = 0

    def write_byte_data(self, addr, reg, value):
        pass

    def read_i2c_block_data(self, addr, reg, length):
        return [self.value >> 8 & 0xFF, self.value & 0xFF]

    def set_acceleration(self, new_value):
        self.value = new_value

camera_device_id = 0

def start_recording(duration=10):
    script_directory = os.path.dirname(__file__)
    video_directory = os.path.join(script_directory, 'video')
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)
    
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(video_directory, f'video_{current_time}.mp4')
    
    cap = cv2.VideoCapture(camera_device_id)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("카메라를 시작할 수 없습니다.")
            return None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, 30.0, (width, height))

    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break
    except Exception as e:
        print(f"예외 발생: {e}")
    finally:
        cap.release()
        out.release()

    return output_filename

def upload_file_to_ftp(file_path):
    ftp_info = read_ftp_config()
    try:
        ftp = FTP(ftp_info['ftp_address'])
        ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
        with open(file_path, 'rb') as file:
            ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}{file_path}", file)
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
