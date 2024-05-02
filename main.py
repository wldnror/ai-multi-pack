import socket
import subprocess
import threading
import re
import time

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode().strip()
        ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
        return ip_address
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return None

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

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
        time.sleep(1)  # 프로세스 종료를 기다림
        force_release_camera()  # 카메라 자원 해제 시도
    except subprocess.CalledProcessError:
        print("Recording process not found.")
        force_release_camera()

def force_release_camera():
    try:
        # /dev/video0를 사용 중인 프로세스 찾기
        camera_process = subprocess.check_output(['fuser', '/dev/video0']).decode().strip()
        if camera_process:
            # 카메라를 사용 중인 프로세스 강제 종료
            subprocess.run(['kill', '-9', camera_process])
            print("Camera resource forcefully released.")
    except Exception as e:
        print(f"Failed to release camera resource: {e}")

def send_status(sock, ip, port, message):
    try:
        sock.sendto(message.encode(), (ip, port))
        print(f"Sent message: {message} to {ip}:{port}")
    except Exception as e:
        print(f"Failed to send message: {e}")

def run_udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    ip_sent = False

    while True:
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        send_status(sock, broadcast_ip, udp_port, recording_status)
        time.sleep(1)

        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"메시지 수신됨: {message} from {addr}")

            if message == "REQUEST_IP" and not ip_sent:
                ip_address = get_ip_address()
                if ip_address:
                    send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
                    ip_sent = True
            elif message == "CONNECTION_SUCCESS":
                print("클라이언트로부터 연결 확인됨. IP 브로드캐스트 중지.")
                ip_sent = True
            elif message == "START_RECORDING":
                start_recording()
            elif message == "STOP_RECORDING":
                stop_recording()

        except socket.timeout:
            continue

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
