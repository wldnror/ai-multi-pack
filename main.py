import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time
from queue import Queue

# 명령 처리 큐 생성
command_queue = Queue()

def command_processor():
    """ 명령을 처리하는 함수 """
    while True:
        command = command_queue.get()
        if command == "START_RECORDING":
            start_recording()
        elif command == "STOP_RECORDING":
            stop_recording()
        command_queue.task_done()

async def notify_status(websocket, path):
    """ WebSocket을 통해 녹화 상태를 실시간으로 알림 """
    while True:
        await asyncio.sleep(1)
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        await websocket.send(recording_status)

def udp_server():
    """ UDP 서버를 통해 외부 명령을 수신하는 함수 """
    udp_ip = "0.0.0.0"
    udp_port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    while True:
        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"메시지 수신됨: {message} from {addr}")
            command_queue.put(message)  # 수신된 메시지를 명령 큐에 추가
        except socket.timeout:
            continue

def get_ip_address():
    """ IP 주소를 가져오는 함수 """
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode().strip()
        ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
        return ip_address
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return None

def process_exists(process_name):
    """ 특정 프로세스가 실행 중인지 확인하는 함수 """
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_recording():
    """ 녹화를 시작하는 함수 """
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    return "RECORDING"

def stop_recording():
    """ 녹화를 중지하는 함수 """
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
        time.sleep(1)  # 프로세스 종료를 기다림
    except subprocess.CalledProcessError:
        print("Recording process not found.")

def main():
    """ 메인 함수에서 WebSocket 서버와 UDP 서버를 실행 """
    loop = asyncio.get_event_loop()
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()
    command_thread = threading.Thread(target=command_processor)
    command_thread.start()
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
