import socket
import subprocess
import threading
import os
import re
import signal

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
    print("Recording process started.")

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

def run_udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    print("UDP server has started. Listening...")

    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode().strip()
        print(f"Received message: {message} from {address}")

        if message == "START_RECORDING":
            if not process_exists('black_box/main.py'):
                print("Starting the recording process...")
                start_process()
            send_recording_status(sock, address, True)
        elif message == "STOP_RECORDING":
            if process_exists('black_box/main.py'):
                print("Stopping the recording process...")
                stop_process()
            send_recording_status(sock, address, False)

        raspberry_pi_ip = get_ip_address()
        if raspberry_pi_ip:
            response = f"{raspberry_pi_ip} 입니다"
            sock.sendto(response.encode(), address)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
