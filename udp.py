import socket
import dns.resolver
import dns.exception
import dns.query
import dns.tsigkeyring
import dns.update
import dns.zone

def register_service(service_name, port):
    # DNS 업데이트
    update = dns.update.Update('local.')
    update.add('_my_udp_service._udp', 60, 'SRV', f'0 0 {port} {socket.gethostname()}.local.')

    try:
        # mDNS 서버로 업데이트 전송
        response = dns.query.udp(update, '224.0.0.251')
        print(response)
    except dns.exception.Timeout:
        print('mDNS update timeout')

# UDP 서버를 실행할 호스트와 포트
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 수신
PORT = 12345      # 서비스를 제공할 포트

# 소켓 생성 (IPv4, UDP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f'Server is listening on {HOST}:{PORT}')

# 서비스 등록
register_service('_my_udp_service._udp', PORT)

# 무한 루프로 UDP 메시지 수신 대기
while True:
    # 데이터와 클라이언트 주소 수신
    data, client_address = server_socket.recvfrom(1024)
    print(f'Received message from {client_address}: {data.decode()}')
