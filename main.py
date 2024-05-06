import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time
from queue import Queue

# 명령 처리를 위한 큐
command_queue = Queue()

def process_exists(process_name):
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    return "RECORDING"

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
        time.sleep(1)  # 프로세스 종료를 기다림
    except subprocess.CalledProcessError:
        print("Recording process not found.")
    finally:
        return "NOT_RECORDING"

def command_processor():
    while True:
        command = command_queue.get()
        if command == "START_RECORDING":
            start_recording()
        elif command == "STOP_RECORDING":
            stop_recording()
        elif command == "EXIT":
            break
        command_queue.task_done()

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
            command_queue.put(message)  # 수신된 메시지를 명령 큐에 추가
        except socket.timeout:
            continue

async def notify_status(websocket, path):
    while True:
        await asyncio.sleep(1)
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        await websocket.send(recording_status)

def main():
    processor_thread = threading.Thread(target=command_processor)
    processor_thread.start()

    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()

    loop = asyncio.get_event_loop()
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
