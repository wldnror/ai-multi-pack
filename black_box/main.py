import os
import time
import configparser
from ftplib import FTP
import subprocess

def test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
    try:
        with FTP(ftp_address) as ftp:
            ftp.login(ftp_username, ftp_password)
            # 경로 존재 여부 확인
            try:
                ftp.cwd(ftp_target_path)  # 해당 경로로 이동 시도
                print("FTP 경로 접근 성공!")
            except Exception as e:
                # 경로가 존재하지 않을 경우, 생성 시도
                try:
                    ftp.mkd(ftp_target_path)  # 경로 생성
                    ftp.cwd(ftp_target_path)  # 생성 후 경로로 이동
                    print("경로가 없어 새로 생성했습니다.")
                except Exception as e:
                    print(f"경로 생성 실패: {e}")
                    return False
            return True
    except Exception as e:
        print(f"FTP 접속 실패: {e}")
        return False

# 설정 파일에서 FTP 정보를 읽어옴
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

def start_ffmpeg_recording(duration=30):
    output_directory = os.path.join(os.path.dirname(__file__), 'video')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')

    command = [
        'ffmpeg',
        '-f', 'v4l2',
        '-framerate', '60',
        '-video_size', '1920x1080',
        '-i', '/dev/video0',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-crf', '28',
        '-t', str(duration),
        output_filename
    ]
    subprocess.run(command)
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

check_config_exists()
try:
    while True:
        input_value = int(input("가속도 값 입력 (0-65535): "))
        if input_value > 15000:  # 예시: 가속도 임계값을 초과할 경우
            print("충격 감지! 녹화 시작")
            output_file = start_ffmpeg_recording(30)
            if output_file:
                upload_file_to_ftp(output_file)
        time.sleep(0.1)
except KeyboardInterrupt:
    print("테스트 종료.")
