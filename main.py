import socket
import subprocess
import re

def get_ip_address():
    try:
        # 'hostname -I' 명령을 통해 라즈베리 파이의 현재 IP 주소를 가져옵니다
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        # 정규 표현식을 사용하여 유효한 IP 주소를 추출합니다
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

def send_command_to_black_box(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 5002))  # 'localhost'와 포트 5002에 연결
        s.sendall(command.encode())  # 명령어를 인코딩하여 보냄

# UDP 서버 설정
udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신하도록 설정
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, address = sock.recvfrom(1024)  # 버퍼 크기는 1024 바이트입니다
    message = data.decode().strip()
    print(f"수신된 메시지: {message} from {address}")

    # 버튼 0001에서 0012까지 처리
    if message.startswith("00"):
        print(f"버튼 {message}가 눌렸습니다.")
        send_command_to_black_box(message)  # 라즈베리 파이 내부 또는 연결된 다른 디바이스에서 처리
        continue

    raspberry_pi_ip = get_ip_address()
    if data and raspberry_pi_ip:
        response = f"{raspberry_pi_ip} 입니다"
        sock.sendto(response.encode(), address)

    # 녹화 시작 및 중지 제어
    if message == "start recording":
        send_command_to_black_box('start')
    elif message == "stop recording":
        send_command_to_black_box('stop')

sock.close()
