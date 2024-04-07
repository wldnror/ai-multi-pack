import socket

UDP_IP = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
UDP_PORT = 12345  # 안드로이드 앱에서 사용하는 포트와 동일

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 소켓 생성
sock.bind((UDP_IP, UDP_PORT))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)  # 버퍼 크기는 1024 바이트
    print(f"수신된 메시지: {data} from {addr}")
    # 여기에서 받은 데이터를 처리하거나 원하는 동작을 수행합니다.
