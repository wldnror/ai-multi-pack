import os
import time
import configparser
from ftplib import FTP
import subprocess
from collections import deque
import smbus
import math
import threading

# MPU-6050 센서 초기 설정
power_mgmt_1 = 0x6b
bus = smbus.SMBus(1)  # 라즈베리 파이의 I2C 버스 사용
address = 0x68        # MPU-6050의 I2C 주소

def read_word_2c(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

def get_acceleration():
    bus.write_byte_data(address, power_mgmt_1, 0)
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
                return True
            except Exception as e:
                ftp.mkd(ftp_target_path)
                ftp.cwd(ftp_target_path)
                print("경로가 없어 새로 생성했습니다.")
                return True
    except Exception as e:
        print(f"FTP 접속 실패: {e}")
        return False

def init_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
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
            print("FTP 설정이 저장되었습니다.")
        else:
            print("FTP 정보가 잘못되었습니다. 다시 확인해주세요.")
    else:
        config.read(config_file_path)
        print("기존 FTP 설정을 불러왔습니다.")
    return config

def read_ftp_config():
    config = init_ftp_config()
    return config['FTP']

def start_ffmpeg_recording(output_filename, duration):
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
        '-y',  # overwrite existing file without asking
        output_filename
    ]
    subprocess.Popen(command)  # Use Popen to not block execution

def capture_event(video_files, timestamp):
    start_time = timestamp - 30  # Capture 30 seconds before the impact
    event_filename = os.path.join(video_files, f'event_{time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime(start_time))}.mp4')
    start_ffmpeg_recording(event_filename, 60)  # Record 60 seconds starting 30 seconds before the impact
    return event_filename

def upload_file_to_ftp(file_path):
    ftp_info = read_ftp_config()
    try:
        with FTP(ftp_info['ftp_address']) as ftp:
            ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
            with open(file_path, 'rb') as file:
                ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}/{os.path.basename(file_path)}", file)
            print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
    except Exception as e:
        print(f"파일 업로드 중 오류 발생: {e}")

def monitor_impacts():
    video_files = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(video_files):
        os.makedirs(video_files)
    last_time_recorded = time.time()
    while True:
        acceleration = get_acceleration()
        if any(abs(a) > 1.5 for a in acceleration):
            print("충격 감지! 이벤트 저장 및 업로드 시작")
            event_filename = capture_event(video_files, last_time_recorded)
            upload_file_to_ftp(event_filename)
        time.sleep(1)  # Check acceleration every second

if __name__ == "__main__":
    monitor_impacts()
