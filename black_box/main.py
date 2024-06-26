import os
import time
import shutil
import smbus
import configparser
from ftplib import FTP
import subprocess
import threading
from threading import Thread, Lock
from queue import Queue
import asyncio
import socket

# MPU-6050 설정
bus = smbus.SMBus(1)  # Raspberry Pi의 I2C 인터페이스 사용
address = 0x68       # MPU-6050의 I2C 주소

# 파일 상태 관리 및 가속도 이전 값 저장을 위한 전역 변수
last_x, last_y, last_z = 0, 0, 0
copied_files_list = set()  # 복사된 파일 목록 관리

# 녹화 및 업로드 관리
queue = Queue()
lock = Lock()

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
    script_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    config.read(config_file_path)
    return config['FTP']

def init_ftp_config():
    config = configparser.ConfigParser()
    script_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
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
    script_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP 설정 파일이 없습니다. 설정을 시작합니다.")
        init_ftp_config()
    else:
        print("기존의 FTP 설정을 불러옵니다.")

class Recorder:
    def __init__(self):
        self.process = None
        self.recording_thread = None
        self.should_stop = False

    def _monitor_recording(self):
        while True:
            output = self.process.stderr.readline()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                print(output.strip())
            if self.should_stop:
                self.process.terminate()
                break

    def start_recording(self, output_filename, duration=60):
        self.should_stop = False
        if not self.process:
            command = [
                'ffmpeg',
                '-f', 'v4l2',
                '-framerate', '60',  # 프레임률 설정
                '-video_size', '1280x720',  # 해상도를 720p로 설정
                '-i', '/dev/video0',
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-crf', '18',
                '-t', str(duration),
                output_filename
            ]
            self.process = subprocess.Popen(command, stderr=subprocess.PIPE, text=True)
            self.recording_thread = Thread(target=self._monitor_recording)
            self.recording_thread.start()

    def stop_recording(self):
        if self.process:
            self.should_stop = True
            self.recording_thread.join()
            self.process = None
            print("녹화가 종료되었습니다.")

recorder = Recorder()

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
                        # 경로 및 파일 이름을 안전하게 처리
                        target_path = f"{ftp_info['ftp_target_path']}/{os.path.basename(file_path)}"
                        ftp.storbinary(f"STOR {target_path}", file)
                    print(f"파일 {file_path}가 성공적으로 업로드되었습니다.")
            except Exception as e:
                print(f"파일 업로드 중 오류 발생: {e}")
        else:
            print(f"파일 {file_path} 생성 실패 후 여러 차례 시도 끝에 포기했습니다.")

        queue.task_done()

def manage_video_files():
    script_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    output_directory = os.path.join(script_directory, 'black_box', '상시녹화')
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

def read_acceleration(addr):
    raw_data = bus.read_i2c_block_data(addr, 0x3B, 6)
    x = (raw_data[0] << 8) + raw_data[1]
    y = (raw_data[2] << 8) + raw_data[3]
    z = (raw_data[4] << 8) + raw_data[5]
    if x > 32767: x -= 65536
    if y > 32767: y -= 65536
    if z > 32767: z -= 65536
    return x, y, z

def init_sensor():
    bus.write_byte_data(address, 0x6B, 0)  # 장치 활성화

def detect_impact(x, y, z, threshold):
    global last_x, last_y, last_z
    delta_x = abs(x - last_x)
    delta_y = abs(y - last_y)
    delta_z = abs(z - last_z)
    last_x, last_y, last_z = x, y, z
    impact_detected = (delta_x + delta_y + delta_z) > threshold
    if impact_detected:
        print(f"충격 감지: Δx={delta_x}, Δy={delta_y}, Δz={delta_z}")
    return impact_detected

def is_file_ready(filepath, timeout=10):
    initial_size = os.path.getsize(filepath)
    time.sleep(1)
    for _ in range(timeout):
        size = os.path.getsize(filepath)
        if size == initial_size:
            return True
        initial_size = size
        time.sleep(1)
    return False

def copy_last_two_videos(input_directory, output_directory, impact_time):
    if not os.path.exists(input_directory):
        print(f"입력 디렉토리가 존재하지 않습니다: {input_directory}")
        return

    video_files = [
        f for f in os.listdir(input_directory)
        if f.endswith('.mp4')
    ]
    video_files = sorted(
        video_files,
        key=lambda x: os.path.getmtime(os.path.join(input_directory, x)),
        reverse=True
    )

    if len(video_files) < 2:
        print("충격 감지 시점에 저장된 상시녹화 파일이 충분하지 않습니다.")
        return

    files_to_copy = video_files[:2]  # 최신 두 개의 파일

    for file in files_to_copy:
        file_path = os.path.join(input_directory, file)
        file_mod_time = os.path.getmtime(file_path)
        file_identifier = (file, file_mod_time)
        if is_file_ready(file_path) and file_identifier not in copied_files_list:
            dst = os.path.join(output_directory, f"충격녹화_{impact_time}_{file}")
            shutil.copy(file_path, dst)
            copied_files_list.add(file_identifier)
            print(f"파일 {file}이 {dst}로 복사되었습니다.")
            queue.put(dst)

def monitor_impact(threshold, input_directory, output_directory):
    init_sensor()
    try:
        while True:
            x, y, z = read_acceleration(address)
            if detect_impact(x, y, z, threshold):
                current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                copy_last_two_videos(input_directory, output_directory, current_time)
            time.sleep(1)
    except KeyboardInterrupt:
        print("모니터링 중단")

def record_and_upload():
    script_directory = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    input_directory = os.path.join(script_directory, 'black_box', '상시녹화')
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)
    
    while True:
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = os.path.join(input_directory, f'video_{current_time}.mp4')

        print(f"녹화 시작: {current_time}")
        recorder.start_recording(output_filename, 60)

        time.sleep(60)
        recorder.stop_recording()

        manage_video_files()

def udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 5001
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    while True:
        try:
            sock.settimeout(10)  # 타임아웃을 10초로 설정
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"메시지 수신됨: {message} from {addr}")  # 수신된 메시지와 발신자 주소 출력

            if message == "START_RECORDING":
                print("녹화 시작 명령 수신")
                recorder.start_recording(os.path.join(os.path.dirname(__file__), 'black_box', '상시녹화', f'video_{time.strftime("%Y-%m-%d_%H-%M-%S")}.mp4'), 60)
                sock.sendto("RECORDING".encode(), addr)
                print("녹화 상태 응답 전송: RECORDING")
            elif message == "STOP_RECORDING":
                print("녹화 중지 명령 수신")
                recorder.stop_recording()
                sock.sendto("NOT_RECORDING".encode(), addr)
                print("녹화 상태 응답 전송: NOT_RECORDING")
            elif message == "REQUEST_RECORDING_STATUS":
                print("녹화 상태 요청 수신")
                response_message = "RECORDING" if recorder.process else "NOT_RECORDING"
                sock.sendto(response_message.encode(), addr)
                print(f"녹화 상태 응답 전송: {response_message}")
            else:
                print(f"알 수 없는 메시지: {message}")
        except socket.timeout:
            print("타임아웃 발생")
            continue
        except Exception as e:
            print(f"예외 발생: {e}")

def main():
    check_config_exists()

    # 스레드 시작
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()
    uploader_thread = Thread(target=upload_worker)
    uploader_thread.start()
    record_thread = Thread(target=record_and_upload)
    record_thread.start()
    impact_monitor_thread = Thread(target=monitor_impact, args=(2000, os.path.abspath('black_box/상시녹화'), os.path.abspath('black_box/충격녹화')))
    impact_monitor_thread.start()

    record_thread.join()
    queue.put(None)
    uploader_thread.join()

if __name__ == "__main__":
    main()
