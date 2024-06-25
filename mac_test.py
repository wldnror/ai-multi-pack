import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time

current_mode = 'manual'  # 초기 모드 설정
connected_clients = set()  # 클라이언트 세션 저장을 위한 집합

def get_ip_address():
    try:
        result = subprocess.check_output(["ipconfig", "getifaddr", "en0"]).decode().strip()
        return result
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return None

def process_exists(process_name):
    try:
        process_list = subprocess.check_output(['ps', 'aux']).decode()
        if process_name in process_list:
            return True
        return False
    except Exception as e:
        print(f"프로세스 확인 중 오류 발생: {e}")
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    else:
        print("녹화 이미 진행 중.")
    return "RECORDING"

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("녹화 중지.")
    except subprocess.CalledProcessError:
        print("녹화 프로세스를 찾을 수 없습니다.")
    finally:
        return "NOT_RECORDING"

def send_status(sock, ip, port, message):
    try:
        ip_address = get_ip_address()
        if ip_address:
            message_with_ip = f"IP:{ip_address} - {message}"
            sock.sendto(message_with_ip.encode(), (ip, port))
        else:
            print("IP 주소를 가져오는 데 실패했습니다.")
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

async def notify_status(websocket, path):
    global connected_clients
    connected_clients.add(websocket)
    try:
        last_status = None
        while True:
            await asyncio.sleep(1)
            recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
            if recording_status != last_status:
                await websocket.send(recording_status)
                print(f"상태 업데이트 전송: {recording_status}")
                last_status = recording_status

    finally:
        connected_clients.remove(websocket)

def udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    def handle_message(data, addr):
        message = data.decode().strip()

        if message == "Right Blinker Activated" and current_mode == 'manual':
            print("오른쪽 블링커 활성화됨")
        elif message == "Left Blinker Activated" and current_mode == 'manual':
            print("왼쪽 블링커 활성화됨")
        elif message == "REQUEST_IP":
            ip_address = get_ip_address()
            if ip_address:
                send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")

    while True:
        try:
            sock.settimeout(0.1)
            data, addr = sock.recvfrom(1024)
            handle_message(data, addr)
        except socket.timeout:
            continue
    return sock

async def main():
    loop = asyncio.get_event_loop()
    sock = udp_server()
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()
    
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
