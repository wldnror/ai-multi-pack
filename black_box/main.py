import os
import time
import configparser
from ftplib import FTP
import subprocess
from threading import Thread, Lock
from queue import Queue
import socket
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
            print(f"녹화 시작됨: {output_filename}")

    def stop_recording(self):
        if self.process:
            self.process.send_signal(signal.SIGTERM)
            self.process.wait()
            self.process = None
            print("녹화 중지됨")

def handle_commands(recorder):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5002))
    server_socket.listen(1)
    print("Control server listening on port 5002.")

    while True:
        client_socket, addr = server_socket.accept()
        with client_socket:
            command = client_socket.recv(1024).decode('utf-8').strip()
            if command == 'start':
                recorder.start_recording('output.mp4')
            elif command == 'stop':
                recorder.stop_recording()

def start_tcp_server(recorder):
    server_thread = Thread(target=handle_commands, args=(recorder,))
    server_thread.daemon = True
    server_thread.start()
    return server_thread

def main():
    recorder = Recorder()
    tcp_server_thread = start_tcp_server(recorder)
    tcp_server_thread.join()

if __name__ == "__main__":
    main()
