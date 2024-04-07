import socket

udp_ip = "0.0.0.0"
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)
    volume = int(data.decode())
    print(f"수신된 볼륨: {volume} from {addr}")
    # 여기에서 볼륨에 따라 LED를 조절하는 로직을 추가할 수 있습니다.
