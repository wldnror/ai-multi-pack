import os
import time
import configparser
from ftplib import FTP
import subprocess
from collections import deque
import smbus
import math

# MPU-6050 센서 초기 설정
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1)  # 라즈베리 파이의 I2C 버스 사용
address = 0x68        # MPU-6050의 I2C 주소

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a, b):
    return math.sqrt((a * a) + (b * b))

def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)

def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)

def get_acceleration():
    bus.write_byte_data(address, power_mgmt_1, 0)  # 센서 깨우기
    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)
    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0
    return accel_xout_scaled, accel_yout_scaled, accel_zout_scaled

def test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
    try:
        with FTP(ftp_address) as ftp:
            ftp.login(ftp_username, ftp_password)
            try:
                ftp.cwd(ftp_target_path)
                print("FTP 경로 접근 성공!")
            except Exception as e:
                try:
                    ftp.mkd(ftp_target_path)
                    ftp.cwd(ftp_target_path)
                    print("경로가 없어 새로 생성했습니다.")
                except Exception as e:
                    print(f"경로 생성 실패: {e}")
                    return False
            return True
    except Exception as e:
        print(f"FTP 접속 실패: {e}")
        return False

def init_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    while True:
        ftp_address = input('FTP 주소 입력: ')
        ftp_username = input('FTP 사용자 이름 입력: ')
        ftp_password = input('FTP 비밀번호 입력: ')
        ftp_target_path = input('FTP 대상 경로 입력: ')
        if test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
            config['FTP'] = {
                'ftp_address': ftp_address,
                'ftp_username': ftp_username,
                'ftp_password': ftp_password,
                'ftp_target_path': ftp_target_path
            }
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)
            break
        else:
            print("잘못된 FTP 정보입니다. 다시 입력해주세요.")

def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

def start_ffmpeg_recording(duration=60):
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-framerate', '30',
        '-video_size', '1920x1080',
        '-i', '/dev/video0',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', '18',
        '-t', str(duration),
        output_filename
    ]
    subprocess.run(command)
    return output_filename

def upload_file_to_ftp(file_path):
    try:
        ftp_info = read_ftp_config()
        with FTP(ftp_info['ftp_address']) as ftp:
            ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
            with open(file_path, 'rb') as file:
                ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}/{os.path.basename(file_path)}", file)
            print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")

def main():
    video_files = deque(maxlen=100)  # 최대 100개의 파일을 유지
    try:
        while True:
            output_file = start_ffmpeg_recording(60)
            video_files.append(output_file)
            if len(video_files) > 100:
                os.remove(video_files.popleft())
            x, y, z = get_acceleration()  # 센서 데이터 읽기
            if abs(x) > 1.5 or abs(y) > 1.5 or abs(z) > 1.5:  # 가속도 임계값 초과 감지
                print("충격 감지! 이전 파일 업로드")
                if len(video_files) > 1:
                    upload_file_to_ftp(video_files[-2])
            time.sleep(60)  # 1분 간격으로 계속 녹화
    except KeyboardInterrupt:
        print("테스트 종료.")

if __name__ == "__main__":
    main()
