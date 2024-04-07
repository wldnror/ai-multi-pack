import socket

# UDP 서버 설정
UDP_IP = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
UDP_PORT = 12345     # 안드로이드 앱과 동일한 포트 번호 사용

# UDP 소켓 생성
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("UDP 서버가 시작되었습니다. 대기 중...")

# 클라이언트로부터 데이터 수신 및 응답
while True:
    data, addr = sock.recvfrom(1024)  # 버퍼 크기는 1024 바이트
    print(f"수신된 메시지: {data} from {addr}")
    # 수신한 데이터에 대한 추가 처리를 여기에 구현합니다.
