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

def create_impact_directory(ftp, base_path, impact_time):
    # 충격 감지 시 새 디렉토리 생성
    new_dir = f"{base_path}/Impact_{impact_time}"
    try:
        ftp.cwd(new_dir)  # 시도: 디렉토리가 이미 있는지 확인
    except:
        ftp.mkd(new_dir)  # 없으면 생성
        ftp.cwd(new_dir)  # 생성된 디렉토리로 이동
    return new_dir

def upload_impact_videos(queue, output_directory, current_time):
    video_files = sorted(os.listdir(output_directory), key=lambda x: os.path.getctime(os.path.join(output_directory, x)))
    current_index = video_files.index(f'video_{current_time}.mp4')
    files_to_upload = []
    if current_index > 0:
        files_to_upload.append(video_files[current_index - 1])
    files_to_upload.append(video_files[current_index])
    if current_index + 1 < len(video_files):
        files_to_upload.append(video_files[current_index + 1])

    ftp_info = read_ftp_config()
    with FTP(ftp_info['ftp_address']) as ftp:
        ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
        impact_dir = create_impact_directory(ftp, ftp_info['ftp_target_path'], current_time)

        for file in files_to_upload:
            local_path = os.path.join(output_directory, file)
            remote_path = f"{impact_dir}/{file}"
            with open(local_path, 'rb') as file_content:
                ftp.storbinary(f"STOR {remote_path}", file_content)
            print(f"파일 {file}가 {impact_dir}에 성공적으로 업로드되었습니다.")


def init_mpu6050(bus, address):
    bus.write_byte_data(address, PWR_MGMT_1, 0)

def read_acceleration(bus, address):
    raw_data = bus.read_i2c_block_data(address, ACCEL_XOUT_H, 6)
    accel_x = (raw_data[0] << 8) | raw_data[1]
    accel_y = (raw_data[2] << 8) | raw_data[3]
    accel_z = (raw_data[4] << 8) | raw_data[5]
    return (accel_x, accel_y, accel_z)

def detect_impact(acceleration, threshold=15000):
    x, y, z = acceleration
    if abs(x) > threshold or abs(y) > threshold or abs(z) > threshold:
        return True
    return False

# FTP 연결 및 설정
def test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
    try:
        with FTP(ftp_address) as ftp:
            ftp.login(ftp_username, ftp_password)
            if ftp.cwd(ftp_target_path):
                print("FTP 경로 접근 성공!")
            else:
                ftp.mkd(ftp_target_path)
                ftp.cwd(ftp_target_path)
                print("경로가 없어 새로 생성했습니다.")
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
        print("FTP 설정 파일 생성 완료.")
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

def upload_impact_videos(queue, output_directory, current_time):
    video_files = sorted(os.listdir(output_directory), key=lambda x: os.path.getctime(os.path.join(output_directory, x)))
    current_index = video_files.index(f'video_{current_time}.mp4')
    files_to_upload = []
    if current_index > 0:
        files_to_upload.append(video_files[current_index - 1])
    files_to_upload.append(video_files[current_index])
    if current_index + 1 < len(video_files):
        files_to_upload.append(video_files[current_index + 1])

    for file in files_to_upload:
        queue.put(os.path.join(output_directory, file))

def record_and_upload(bus):
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
        start_ffmpeg_recording(output_filename, duration=60)
        manage_video_files()

        acceleration = read_acceleration(bus, DEVICE_ADDRESS)
        if detect_impact(acceleration):
            print("충격 감지됨! 관련 비디오 처리 시작...")
            upload_impact_videos(queue, output_directory, current_time)

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
