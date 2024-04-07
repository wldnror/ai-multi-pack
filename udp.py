import socket
import fcntl
import struct

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', bytes(ifname[:15], 'utf-8'))
        )[20:24])
    except Exception as e:
        print("Error getting IP address:", str(e))
        return None

udp_port = 12345

# 라즈베리파이에 연결된 네트워크 인터페이스의 IP 주소 가져오기
raspberry_pi_ip = get_ip_address("wlan0")  # 수정: 실제 네트워크 인터페이스 이름 사용

if raspberry_pi_ip:
    print("라즈베리 파이의 IP 주소:", raspberry_pi_ip)

# UDP 소켓 생성 및 연결
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((raspberry_pi_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)  # 버퍼 크기는 1024 바이트
    print(f"수신된 메시지: {data} from {addr}")
