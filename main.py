import socket
import subprocess
import threading
import re
import time

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode().strip()
        ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
        return ip_address
    except Exception as e:
        print(f"Failed to get IP address: {e}")
        return None

def process_exists(process_name):
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("Recording started.")

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
    except subprocess.CalledProcessError:
        print("Recording process not found.")

def send_status(sock, ip, port, message):
    sock.sendto(message.encode(), (ip, port))
    print(f"Sent message: {message} to {ip}:{port}")

def run_udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP server has started. Listening...")

    ip_sent = False

    while True:
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        send_status(sock, broadcast_ip, udp_port, recording_status)
        time.sleep(1)

        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received message: {message} from {addr}")

            if message == "REQUEST_IP" and not ip_sent:
                ip_address = get_ip_address()
                if ip_address:
                    send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
                    ip_sent = True
            elif message == "CONNECTION_SUCCESS":
                print("Connection confirmed by client. No more IP broadcasts.")
                ip_sent = True
            elif message == "START_RECORDING":
                start_recording()
            elif message == "STOP_RECORDING":
                stop_recording()

        except socket.timeout:
            continue

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
