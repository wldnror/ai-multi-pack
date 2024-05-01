import socket
import threading
from queue import Queue
import subprocess
import time
import os
import configparser
from ftplib import FTP

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
    return subprocess.Popen(command)

def stop_ffmpeg_recording(process):
    if process:
        process.terminate()

class CommandServer:
    def __init__(self, host='localhost', port=5002):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        self.recording_process = None

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            elif data == 'start':
                if not self.recording_process:
                    print("Starting recording...")
                    current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                    output_directory = os.path.join(os.path.dirname(__file__), '상시녹화')
                    output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
                    self.recording_process = start_ffmpeg_recording(output_filename)
            elif data == 'stop':
                if self.recording_process:
                    print("Stopping recording...")
                    stop_ffmpeg_recording(self.recording_process)
                    self.recording_process = None
        client_socket.close()

    def run(self):
        print("Command server running...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connected by {addr}")
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

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

if __name__ == "__main__":
    cmd_server = CommandServer()
    server_thread = threading.Thread(target=cmd_server.run)
    server_thread.start()

    queue = Queue()
    uploader_thread = threading.Thread(target=upload_worker)
    uploader_thread.start()

    print("System is ready for commands.")
