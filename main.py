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
    last_ip_sent_time = time.time()

    while True:
        current_time = time.time()
        
        # Send recording status every second
        if current_time - last_ip_sent_time >= 1:
            recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
            send_status(sock, broadcast_ip, udp_port, recording_status)

        # Send IP address if not confirmed or on 5-second intervals if not acknowledged
        if not ip_sent or (current_time - last_ip_sent_time >= 5):
            ip_address = get_ip_address()
            if ip_address:
                send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
                last_ip_sent_time = current_time
        
        time.sleep(0.1)  # Adjust the loop delay to manage CPU usage and network traffic

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
