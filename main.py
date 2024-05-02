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
    last_ip_sent_time = 0

    while True:
        if not ip_sent or (time.time() - last_ip_sent_time >= 5):
            ip_address = get_ip_address()
            if ip_address:
                send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
                last_ip_sent_time = time.time()
                ip_sent = True
        
        # Check for incoming messages to confirm connection
        try:
            sock.settimeout(5)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            print(f"Received message: {message} from {addr}")

            # If a specific success message is received, stop sending IP
            if message == "CONNECTION_SUCCESS":
                print("Connection confirmed by client.")
                break

        except socket.timeout:
            print("No response from client, retrying...")
            ip_sent = False

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
