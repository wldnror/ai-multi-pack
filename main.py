import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time
from queue import Queue

command_queue = Queue()  # 명령을 저장할 큐

def command_processor():
    while True:
        command = command_queue.get()
        if command == "START_RECORDING":
            start_recording()
        elif command == "STOP_RECORDING":
            stop_recording()
        command_queue.task_done()

# WebSocket을 통한 실시간 상태 알림
async def notify_status(websocket, path):
    while True:
        await asyncio.sleep(1)
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        await websocket.send(recording_status)

# UDP 서버 처리를 위한 함수
def udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
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
            command_queue.put(message)  # 명령을 큐에 추가
        except socket.timeout:
            continue

# IP 주소 가져오기
def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode().strip()
        ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
        return ip_address
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return None

# 프로세스 존재 확인
def process_exists(process_name):
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

# 녹화 시작
def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    return "RECORDING"

# 녹화 중지
def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
        time.sleep(1)  # 프로세스 종료를 기다림
        force_release_camera()  # 카메라 자원 해제 시도
    except subprocess.CalledProcessError:
        print("Recording process not found.")
        force_release_camera()
    finally:
        return "NOT_RECORDING"

# 카메라 자원 해제
def force_release_camera():
    try:
        camera_process_output = subprocess.check_output(['fuser', '/dev/video0']).decode().strip()
        for pid in camera_process_output.split():
            subprocess.call(['kill', '-9', pid])
        print("Camera resource forcefully released.")
    except Exception as e:
        print(f"Failed to release camera resource: {e}")

# 상태 메시지 전송
def send_status(sock, ip, port, message):
    try:
        sock.sendto(message.encode(), (ip, port))
        print(f"Sent message: {message} to {ip}:{port}")
    except Exception as e:
        print(f"Failed to send message: {e}")
# 메인 함수에서 서버와 명령 처리기를 병렬로 실행
def main():
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
