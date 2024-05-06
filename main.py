import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time

# WebSocket을 통한 실시간 상태 알림
async def notify_status(websocket, path):
    while True:
        await asyncio.sleep(1)  # 상태를 1초마다 확인
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        await websocket.send(recording_status)  # 상태를 WebSocket을 통해 전송
        
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

            if message == "REQUEST_IP":
                ip_address = get_ip_address()
                if ip_address:
                    send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
            elif message == "START_RECORDING":
                recording_status = start_recording()
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "STOP_RECORDING":
                recording_status = stop_recording()
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "REQUEST_RECORDING_STATUS":  # 클라이언트로부터 녹화 상태 요청을 받음
                recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "Right Blinker Activated":
                print("오른쪽 블링커 활성화됨")
                subprocess.call(['python3', 'led/gyro_led_steering.py', 'right_on'])
                send_status(sock, broadcast_ip, udp_port, "오른쪽 블링커 활성화됨")
            elif message == "Left Blinker Activated":
                print("왼쪽 블링커 활성화됨")
                subprocess.call(['python3', 'led/gyro_led_steering.py', 'left_on'])
                send_status(sock, broadcast_ip, udp_port, "왼쪽 블링커 활성화됨")

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

# 메인 함수에서 두 서버를 병렬로 실행
def main():
    loop = asyncio.get_event_loop()
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
