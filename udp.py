import socket

# UDP 서버를 실행할 호스트와 포트
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 수신
PORT = 12345      # 임의의 포트 번호

# 소켓 생성 (IPv4, UDP)
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
    # 소켓을 주소에 바인딩
    server_socket.bind((HOST, PORT))
    print(f'Server is listening on {HOST}:{PORT}')

    # 무한 루프로 UDP 메시지 수신 대기
    while True:
        # 데이터와 클라이언트 주소 수신
        data, client_address = server_socket.recvfrom(1024)
        print(f'Received message from {client_address}: {data.decode()}')
