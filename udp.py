import socket

# UDP 서버를 실행할 호스트와 포트
HOST = '0.0.0.0'  # 모든 네트워크 인터페이스에서 수신
PORT = 12345      # 서비스를 제공할 포트

# 소켓 생성 (IPv4, UDP)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print(f'Server is listening on {HOST}:{PORT}')

# 무한 루프로 UDP 메시지 수신 대기
while True:
    # 데이터와 클라이언트 주소 수신
    data, client_address = server_socket.recvfrom(1024)
    print(f'Received message from {client_address}: {data.decode()}')


import dns
import dns.exception
import dns.query
import dns.tsigkeyring
import dns.update
import dns.zone
import socket

def register_service(service_name, port):
    # 서비스 레코드 생성
    service_record = dns.rdatatype.SRV(
        port=port,
        target=socket.gethostname() + '.local.')  # 라즈베리 파이의 로컬 호스트 이름

    # 서비스 정보 생성
    service_info = dns.rrset.RRset(
        dns.name.from_text(service_name),
        dns.rdataclass.IN,
        service_record)

    # DNS 업데이트
    update = dns.update.Update('local.')
    update.add(service_info)

    try:
        # mDNS 서버로 업데이트 전송
        response = dns.query.tcp(update, '224.0.0.251')
        print(response)
    except dns.exception.Timeout:
        print('mDNS update timeout')

# 서비스 등록
register_service('_my_udp_service._udp', PORT)
