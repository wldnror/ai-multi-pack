import socket
import subprocess
import threading
import os

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

def process_exists():
    try:
        # 'main.py'만 검색하여 프로세스 존재 여부 확인
        result = subprocess.check_output(['pgrep', '-f', 'black_box/main.py'])
        print("Process exists:", result.decode())
        return True
    except subprocess.CalledProcessError:
        print("black_box/main.py is not running.")
        return False

def start_process():
    script_path = os.path.join(os.path.dirname(__file__), 'black_box', 'main.py')
    print("Starting black_box/main.py...")
    subprocess.Popen(['python3', script_path])

def stop_process():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Stopped black_box/main.py successfully.")
    except subprocess.CalledProcessError:
        print("Failed to stop black_box/main.py.")

udp_ip = "0.0.0.0"
udp_port = 12345
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
print("UDP server is up and listening...")

while True:
    data, address = sock.recvfrom(1024)
    message = data.decode().strip()
    print(f"Received message: {message} from {address}")

    if message == "0003":
        if not process_exists():
            start_process()
        else:
            stop_process()

    elif message.startswith("00"):
        print(f"Button {message} was pressed.")

    raspberry_pi_ip = get_ip_address()
    if data and raspberry_pi_ip:
        response = f"{raspberry_pi_ip} is your IP"
        sock.sendto(response.encode(), address)
