import os
import time
import configparser
from ftplib import FTP
import subprocess
from threading import Thread, Lock
from queue import Queue
import signal

class Recorder:
    def __init__(self):
        self.process = None

    def start_recording(self, output_filename, duration=60):
        if not self.process:
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
            self.process = subprocess.Popen(command)
            print(f"Recording started: {output_filename}")

    def stop_recording(self):
        if self.process:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait()
            self.process = None
            print("Recording stopped.")

def test_ftp_connection(ftp_address, ftp_username, ftp_password, ftp_target_path):
    try:
        with FTP(ftp_address) as ftp:
            ftp.login(ftp_username, ftp_password)
            try:
                ftp.cwd(ftp_target_path)
                print("FTP path access successful!")
            except Exception as e:
                try:
                    ftp.mkd(ftp_target_path)
                    ftp.cwd(ftp_target_path)
                    print("Created new directory as it did not exist.")
                except Exception as e:
                    print(f"Failed to create directory: {e}")
                    return False
            return True
    except Exception as e:
        print(f"FTP connection failed: {e}")
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
        ftp_address = input('Enter FTP address: ')
        ftp_username = input('Enter FTP username: ')
        ftp_password = input('Enter FTP password: ')
        ftp_target_path = input('Enter FTP target path: ')
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
            print("Incorrect FTP details. Please re-enter.")

def check_config_exists():
    script_directory = os.path.dirname(__file__)
    config_file_path = os.path.join(script_directory, 'ftp_config.ini')
    if not os.path.exists(config_file_path):
        print("FTP configuration file does not exist. Starting configuration.")
        init_ftp_config()
    else:
        print("Loading existing FTP configuration.")

def manage_video_files():
    output_directory = os.path.join(os.path.dirname(__file__), 'ContinuousRecording')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    with lock:
        video_files = sorted(os.listdir(output_directory), key=lambda x: os.path.getctime(os.path.join(output_directory, x)))
        while len(video_files) > 100:
            file_to_delete = os.path.join(output_directory, video_files.pop(0))
            os.remove(file_to_delete)
            print(f"Deleted file: {file_to_delete}")

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
                    print(f"Successfully uploaded file: {file_path}")
        except Exception as e:
            print(f"Error uploading file: {e}")
        finally:
            queue.task_done()

def record_and_upload():
    recorder = Recorder()
    while True:
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
        output_directory = os.path.join(os.path.dirname(__file__), 'ContinuousRecording')
        output_filename = os.path.join(output_directory, f'video_{current_time}.mp4')
        
        print(f"Starting recording: {current_time}")
        recorder.start_recording(output_filename, 3600)  # 1 hour duration
        
        manage_video_files()
        queue.put(output_filename)

def main():
    check_config_exists()
    uploader_thread = Thread(target=upload_worker)
    uploader_thread.start()

    record_thread = Thread(target=record_and_upload)
    record_thread.start()

    record_thread.join()
    queue.put(None)
    uploader_thread.join()

if __name__ == "__main__":
    main()
