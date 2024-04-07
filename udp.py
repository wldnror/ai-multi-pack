import socket
import fcntl
import struct

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

udp_ip = get_ip_address('wlan0')  # wlan0은 라즈베리 파이의 무선 네트워크 인터페이스 이름입니다. 만약 이와 다른 인터페이스를 사용 중이라면 해당 인터페이스 이름을 사용하세요.
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"수신된 메시지: {data.decode()} from {addr}")

    # 클라이언트(안드로이드 앱)에게 라즈베리 파이의 IP 주소를 보냄
    if data:
        response = f"My IP address is {udp_ip}"
        sock.sendto(response.encode(), addr)
