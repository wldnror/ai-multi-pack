import socket

udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
udp_port = 12345     # 안드로이드 앱과 동일한 포트

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP 소켓 생성
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)  # 버퍼 크기는 1024 바이트
    print(f"수신된 메시지: {data.decode()} from {addr}")
