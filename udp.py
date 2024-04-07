import socket

udp_ip = "0.0.0.0"
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)
    message = data.decode()
    
    # 메시지가 볼륨 정보인지 확인
    try:
        volume = int(message)
        print(f"수신된 볼륨: {volume} from {addr}")
        # 볼륨 정보를 사용하여 LED 조작 등의 로직 추가
    except ValueError:
        # 볼륨 정보가 아닌 다른 메시지 처리
        if message == "Hello Raspberry Pi!":
            response = f"My IP address is {addr[0]}"
            sock.sendto(response.encode(), addr)
        else:
            print(f"알 수 없는 메시지: {message} from {addr}")
