import os
import time
import datetime
import configparser
from ftplib import FTP
import subprocess
from threading import Thread, Lock
from queue import Queue
import smbus2

# 센서 설정 및 데이터 읽기
DEVICE_ADDRESS = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

def init_mpu6050(bus, address):
    bus.write_byte_data(address, PWR_MGMT_1, 0)

def read_acceleration(bus, address):
    raw_data = bus.read_i2c_block_data(address, ACCEL_XOUT_H, 6)
    accel_x = (raw_data[0] << 8) | raw_data[1]
    accel_y = (raw_data[2] << 8) | raw_data[3]
    accel_z = (raw_data[4] << 8) | raw_data[5]
    print(f"Read acceleration data - X: {accel_x}, Y: {accel_y}, Z: {accel_z}")
    return (accel_x, accel_y, accel_z)

def detect_impact(acceleration, threshold=15000):
    x, y, z = acceleration
    print(f"Checking impact - X: {x}, Y: {y}, Z: {z}, Threshold: {threshold}")
    if abs(x) > threshold or abs(y) > threshold or abs(z) > threshold:
        print("Impact detected!")
        return True
    return False

# FTP 연결 및 설정
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

def read_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

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

def check_config_exists():
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP 설정 파일이 없습니다. 설정을 시작합니다.")
        init_ftp_config()
    else:
        print("기존의 FTP 설정을 불러옵니다.")

# 비디오 녹화
def start_ffmpeg_recording(output_filename, duration=60):
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

# 파일 업로드 및 관리
queue = Queue()
lock = Lock()

def upload_worker():
    while True:
        file_path = queue.get()
        if file_path is None:
            break
        try:
            ftp_info = read_ftp_config()
            with FTP(ftp_info['ftp_address']) as ftp:
                ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
                with open(file_path, 'rb') as file:
                    ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}/{os.path.basename(file_path)}", file)
                print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
        except Exception as e:
            print(f"파일 업로드 중 오류 발생: {e}")
        finally:
            queue.task_done()

def manage_video_files():
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with lock:
        video_files = sorted(os.listdir(output_directory), key=lambda x: os.path.getctime(os.path.join(output_directory, x)))
        while len(video_files) > 100:
            file_to_delete = os.path.join(output_directory, video_files.pop(0))
            os.remove(file_to_delete)
            print(f"파일 {file_to_delete}가 삭제되었습니다.")

# 메인 녹화 및 충격 감지 로직
def record_and_upload(bus):
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
        
        print(f"녹화 시작: {current_time}")
        start_ffmpeg_recording(output_filename, duration=60)
        
        manage_video_files()

        # 충격 감지
        acceleration = read_acceleration(bus, DEVICE_ADDRESS)
        if detect_impact(acceleration):
            print("충격 감지됨! 관련 비디오 처리 시작...")
            # 여기에 충격 관련 파일 처리 및 업로드 로직 구현 필요
            def upload_impact_videos(queue, output_directory, current_time):
    video_files = sorted(os.listdir(output_directory), key=lambda x: os.path.getctime(os.path.join(output_directory, x)))
    # 현재 파일을 기준으로 과거, 현재, 미래 파일 경로를 구하기
    current_index = video_files.index(f'video_{current_time}.mp4')
    files_to_upload = []
    if current_index > 0:  # 과거 파일이 존재하는 경우
        files_to_upload.append(video_files[current_index - 1])
    files_to_upload.append(video_files[current_index])  # 현재 파일
    if current_index + 1 < len(video_files):  # 미래 파일이 존재하는 경우
        files_to_upload.append(video_files[current_index + 1])
    
    # 해당 파일들을 업로드 큐에 추가
    for file in files_to_upload:
        queue.put(os.path.join(output_directory, file))

def record_and_upload(bus):
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
        start_ffmpeg_recording(output_filename, duration=60)
        manage_video_files()

        # 충격 감지 및 파일 업로드
        acceleration = read_acceleration(bus, DEVICE_ADDRESS)
        if detect_impact(acceleration):
            print("충격 감지됨! 관련 비디오 처리 시작...")
            upload_impact_videos(queue, output_directory, current_time)
        
        queue.put(output_filename)

        
        queue.put(output_filename)

# 설정 확인 및 센서 초기화
bus = smbus2.SMBus(1)
init_mpu6050(bus, DEVICE_ADDRESS)
check_config_exists()

# 스레드 시작
uploader_thread = Thread(target=upload_worker)
uploader_thread.start()

record_thread = Thread(target=lambda: record_and_upload(bus))
record_thread.start()

record_thread.join()
queue.put(None)
uploader_thread.join()
