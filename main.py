import socket
import subprocess
import re

def get_ip_address():
    try:
        # 'hostname -I' 명령을 통해 라즈베리 파이의 현재 IP 주소를 가져옵니다
        결과 = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        # 정규 표현식을 사용하여 유효한 IP 주소를 추출합니다
        ip_주소들 = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 결과)
        return ip_주소들[0] if ip_주소들 else None
    except subprocess.CalledProcessError:
        return None

def send_command_to_black_box(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 5002))  # 'localhost'와 포트 5002에 연결
        s.sendall(command.encode())  # 명령어를 인코딩하여 보냄

# UDP 서버 설정
udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신하도록 설정
udp_port = 12345

소켓 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
소켓.bind((udp_ip, udp_port))
print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    데이터, 주소 = 소켓.recvfrom(1024)  # 버퍼 크기는 1024 바이트입니다
    print(f"수신된 메시지: {데이터.decode()} from {주소}")

    라즈베리파이_ip = get_ip_address()
    if 데이터 and 라즈베리파이_ip:
        응답 = f"{라즈베리파이_ip} 입니다"
        소켓.sendto(응답.encode(), 주소)

    # 녹화 시작 및 중지 제어
    message = 데이터.decode().strip()
    if message == "start recording":
        send_command_to_black_box('start')
    elif message == "stop recording":
        send_command_to_black_box('stop')

소켓.close()
