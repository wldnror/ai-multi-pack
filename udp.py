# import socket

# udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
# udp_port = 12345

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((udp_ip, udp_port))

# print("UDP 서버가 시작되었습니다. 대기 중...")

# # 라즈베리 파이의 IP 주소 가져오기
# import subprocess
# import re

# def get_ip_address():
#     try:
#         result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
#         ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
#         if ip_addresses:
#             return ip_addresses[0]
#         else:
#             return None
#     except subprocess.CalledProcessError:
#         return None

# raspberry_pi_ip = get_ip_address()

# while True:
#     data, addr = sock.recvfrom(1024)
#     print(f"수신된 메시지: {data.decode()} from {addr}")

#     # 클라이언트(안드로이드 앱)에게 라즈베리 파이의 IP 주소를 보냄
#     if data and raspberry_pi_ip:
#         response = f"My IP address is {raspberry_pi_ip}"
#         sock.sendto(response.encode(), addr)
import socket

udp_ip = "0.0.0.0"  # 모든 인터페이스에서 들어오는 데이터를 수신
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, addr = sock.recvfrom(1024)
    print(f"수신된 오디오 데이터 길이: {len(data)} from {addr}")

    # 여기에서 수신된 오디오 데이터(data)를 처리하는 코드를 추가하면 됩니다.
    # 예를 들어 오디오 데이터를 재생하거나 저장하는 등의 작업을 수행할 수 있습니다.
