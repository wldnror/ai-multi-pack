import socket

udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"수신된 메시지: {data.decode()} from {addr}")

    # 클라이언트(안드로이드 앱)에게 라즈베리 파이의 IP 주소를 보냄
    if data:
        response = f"My IP address is {addr[0]}"
        sock.sendto(response.encode(), addr)
