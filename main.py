import socket
import subprocess
import threading
import os
import re
import signal
import time

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

def process_exists(process_name):
    try:
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_process():
    script_path = os.path.join(os.path.dirname(__file__), 'black_box', 'main.py')
    subprocess.Popen(['python3', script_path])

def stop_process():
    try:
        pids = subprocess.check_output(['pgrep', '-f', 'black_box/main.py']).decode().strip().split()
        for pid in pids:
            os.kill(int(pid), signal.SIGKILL)
            print(f"Process {pid} has been forcefully stopped with SIGKILL.")
    except subprocess.CalledProcessError:
        print("black_box/main.py is not currently running.")

def send_recording_status(sock, address, is_recording):
    message = "RECORDING" if is_recording else "NOT_RECORDING"
    sock.sendto(message.encode(), address)

def send_udp_broadcast():
    udp_ip = "255.255.255.255"
    udp_port = 12345
    message = "RECORDING"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        sock.sendto(message.encode(), (udp_ip, udp_port))
        print(f"Sent message: {message}")
        time.sleep(1)  # 1초마다 메시지 전송

    while True:
        current_status = process_exists('black_box/main.py')
        if current_status != last_sent_status:
            send_recording_status(sock, ('<broadcast>', udp_port), current_status)
            last_sent_status = current_status
        
        raspberry_pi_ip = get_ip_address()
        if raspberry_pi_ip and raspberry_pi_ip != last_ip_address:
            response = f"{raspberry_pi_ip} 입니다"
            sock.sendto(response.encode(), ('<broadcast>', udp_port))
            last_ip_address = raspberry_pi_ip
        
        time.sleep(1)  # Check and send updates every second


if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
