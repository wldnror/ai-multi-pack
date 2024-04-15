import time
import cv2
from ftplib import FTP

# FTP 서버 정보 설정
ftp_address = 'ftp.yourserver.com'
ftp_username = 'your_username'
ftp_password = 'your_password'
ftp_target_path = '/path/to/upload/'  # FTP 서버 상의 파일 업로드 경로

def upload_file_to_ftp(file_path):
    # FTP 서버에 파일을 업로드하는 함수
    ftp = FTP(ftp_address)
    ftp.login(ftp_username, ftp_password)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {ftp_target_path}{file_path}', file)
    ftp.quit()
    print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")

def start_recording(duration=60):
    # 카메라 초기화 및 녹화 설정
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("카메라를 시작할 수 없습니다.")
        return

    output_filename = 'output.avi'
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (640, 480))

    start_time = time.time()
    while (time.time() - start_time) < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # 자원 해제
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return output_filename

# MPU-6050 설정을 모의 객체로 대체
class MockSMBus:
    def __init__(self, bus_number):
        pass
    def write_byte_data(self, addr, reg, value):
        pass
    def read_i2c_block_data(self, addr, reg, length):
        # 테스트를 위한 임의의 가속도 값 반환
        return [0, 0]

bus = MockSMBus(1)
device_address = 0x68
bus.write_byte_data(device_address, 0x6B, 0)

def read_acceleration(axis):
    # 가속도 데이터 읽기
    data = bus.read_i2c_block_data(device_address, axis, 2)
    value = data[0] << 8 | data[1]
    if value > 32767:
        value -= 65536
    return value

threshold = 15000  # 임계값 설정
while True:
    acceleration = read_acceleration(0x3B)  # X축 데이터 읽기
    if abs(acceleration) > threshold:
        print("충격 감지! 녹화 시작")
        # 충격 감지 시점부터 30초 전까지의 영상 녹화
        start_time = time.time()
        while (time.time() - start_time) < 30:
            start_recording(30)

        # 충격 감지 시점부터 30초 후까지의 영상 녹화
        start_time = time.time()
        while (time.time() - start_time) < 30:
            start_recording(30)

        # FTP로 파일 전송
        upload_file_to_ftp('output.avi')
    time.sleep(0.1)
