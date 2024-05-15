import os
import time
import configparser
from ftplib import FTP
import cv2
from threading import Thread, Lock
from queue import Queue

def test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
    try:
        with FTP(ftp_address) as ftp:
            ftp.login(ftp_username, ftp_password)
            try:
                ftp.cwd(ftp_target_path)
                print("FTP 경로 접근 성공!")
            except Exception:
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

class Recorder:
    def __init__(self):
        self.recording = False

    def start_recording(self, output_filename, duration=60):
        self.recording = True
        cap = cv2.VideoCapture(0)  # Use the first camera
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_filename, fourcc, 30.0, (1920, 1080))

        start_time = time.time()
        while self.recording and (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()

    def stop_recording(self):
        self.recording = False

recorder = Recorder()
queue = Queue()
lock = Lock()

def upload_worker():
    while True:
        file_path = queue.get()
        if file_path is None:
            break

        file_ready = False
        attempts = 0
        while not file_ready and attempts < 10:
            if os.path.exists(file_path):
                file_ready = True
            else:
                time.sleep(1)
                attempts += 1

        if file_ready:
            try:
                ftp_info = read_ftp_config()
                with FTP(ftp_info['ftp_address']) as ftp:
                    ftp.login(ftp_info['ftp_username'], ftp_info['ftp_password'])
                    with open(file_path, 'rb') as file:
                        ftp.storbinary(f"STOR {ftp_info['ftp_target_path']}/{os.path.basename(file_path)}", file)
                    print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
            except Exception as e:
                print(f"파일 업로드 중 오류 발생: {e}")
        else:
            print(f"파일 {file_path} 생성 실패 후 여러 차례 시도 끝에 포기했습니다.")

        queue.task_done()

def manage_video_files():
    output_directory = os.path.join(os.path.dirname(__file__), '상시녹화')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with lock:
        video_files = sorted(
            (f for f in os.listdir(output_directory) if os.path.isfile(os.path.join(output_directory, f))),
            key=lambda x: os.path.getctime(os.path.join(output_directory, x))
        )
        while len(video_files) > 100:
            file_to_delete = os.path.join(output_directory, video_files.pop(0))
            os.remove(file_to_delete)
            print(f"파일 {file_to_delete}가 삭제되었습니다.")

def record_and_upload():
    while True:
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_directory = os.path.join(os.path.dirname(__file__), '상시녹화')
        output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')

        print(f"녹화 시작: {current_time}")
        recorder.start_recording(output_filename, 60)

        time.sleep(60)
        recorder.stop_recording()

        manage_video_files()
        queue.put(output_filename)

check_config_exists()

uploader_thread = Thread(target=upload_worker)
uploader_thread.start()

record_thread = Thread(target=record_and_upload)
record_thread.start()

record_thread.join()
queue.put(None)
uploader_thread.join()
