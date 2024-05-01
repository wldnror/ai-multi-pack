import socket
import socketserver
import subprocess
import re
import threading

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print(f"TCP server received: {self.data.decode()} from {self.client_address}")
        # Here you could add any specific logic to handle incoming data
        self.request.sendall(self.data.upper())

def run_tcp_server():
    host, port = "localhost", 5002
    with socketserver.TCPServer((host, port), MyTCPHandler) as server:
        print(f"TCP Server running on {host}:{port}")
        server.serve_forever()

# Start the TCP server in a separate thread
tcp_server_thread = threading.Thread(target=run_tcp_server)
tcp_server_thread.daemon = True
tcp_server_thread.start()

# UDP 서버 설정
udp_ip = "0.0.0.0"
udp_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
print("UDP 서버가 시작되었습니다. 대기 중...")

while True:
    data, address = sock.recvfrom(1024)
    message = data.decode().strip()
    print(f"수신된 메시지: {message} from {address}")

    if message.startswith("00"):
        print(f"버튼 {message}가 눌렸습니다.")
        continue

    raspberry_pi_ip = get_ip_address()
    if data and raspberry_pi_ip:
        response = f"{raspberry_pi_ip} 입니다"
        sock.sendto(response.encode(), address)
