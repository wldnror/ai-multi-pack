import time
import cv2
from ftplib import FTP

# FTP 서버 정보 설정
ftp_address = '79webhard.com'  # "ftp://" 접두사 제거
ftp_username = 'webmaster'
ftp_password = 'adminqwe1@32317J'
ftp_target_path = '/home/video/'  # 실제 파일 업로드 경로로 변경

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

# Logitech BRIO 카메라의 경우 장치 ID를 확인하고 이에 맞게 수정
camera_device_id = 0  # 장치 ID를 0으로 가정합니다.

def start_recording(duration=10):
    cap = cv2.VideoCapture(camera_device_id)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)  # 대체 장치로 다시 시도
        if not cap.isOpened():
            print("카메라를 시작할 수 없습니다.")
            return

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_filename = 'output11.mp4'
    out = cv2.VideoWriter(output_filename, fourcc, 30.0

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
        cv2.destroyAllWindows()
        return output_filename


def upload_file_to_ftp(file_path):
    try:
        ftp = FTP(ftp_address)
        ftp.login(ftp_username, ftp_password)
        with open(file_path, 'rb') as file:
            ftp.storbinary(f'STOR {ftp_target_path}{file_path}', file)
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
