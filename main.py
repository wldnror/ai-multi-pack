# main.py

import subprocess
import re
import threading
import os
import socket

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

def process_exists(process_name):
    try:
        # Use the exact script path
        full_path = os.path.join(os.path.dirname(__file__), process_name)
        subprocess.check_output(['pgrep', '-f', full_path])
        return True
    except subprocess.CalledProcessError:
        return False

def start_process(process_path):
    subprocess.Popen(['python3', process_path])

def send_command_to_process(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(('localhost', 5002))
        s.sendall(command.encode())

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip().decode()
        print(f"TCP server received: {self.data} from {self.client_address}")

        if self.data == "start":
            global recording
            if not process_exists('black_box/main.py'):
                print("black_box/main.py is not running. Starting the process.")
                start_process('black_box/main.py')
            else:
                if not recording:
                    print("Starting recording.")
                    send_command_to_process('start')
                    recording = True
                else:
                    print("Stopping recording.")
                    send_command_to_process('stop')
                    recording = False

def run_tcp_server():
    host, port = "localhost", 5002
    with socketserver.TCPServer((host, port), MyTCPHandler) as server:
        print(f"TCP Server running on {host}:{port}")
        server.serve_forever()

# Start the TCP server in a separate thread
tcp_server_thread = threading.Thread(target=run_tcp_server)
tcp_server_thread.daemon = True
tcp_server_thread.start()

# UDP server setup
udp_ip = "0.0.0.0"
udp_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
print("UDP server has started. Listening...")

recording = False  # Track recording status

while True:
    data, address = sock.recvfrom(1024)
    message = data.decode().strip()
    print(f"Received message: {message} from {address}")

    if message == "0003":
        if not process_exists('black_box/main.py'):
            print("black_box/main.py is not running. Starting the process.")
            start_process('black_box/main.py')
        else:
            if not recording:
                print("Starting recording.")
                send_command_to_process('start')
                recording = True
            else:
                print("Stopping recording.")
                send_command_to_process('stop')
                recording = False
        continue

    if message.startswith("00"):
        print(f"Button {message} pressed.")
        continue

    raspberry_pi_ip = get_ip_address()
    if data and raspberry_pi_ip:
        response = f"This is {raspberry_pi_ip}"
        sock.sendto(response.encode(), address)
