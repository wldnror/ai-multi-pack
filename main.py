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

def process_exists(process_name):
    try:
        # 'pgrep'를 사용하여 프로세스가 실행 중인지 확인합니다.
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_process():
    # 'black_box/main.py' 프로세스를 시작합니다.
    script_path = os.path.join(os.path.dirname(__file__), 'black_box', 'main.py')
    subprocess.Popen(['python3', script_path])

def stop_process():
    try:
        # 프로세스 이름으로 실행 중인 프로세스를 찾아 종료
        pids = subprocess.check_output(['pgrep', '-f', 'black_box/main.py']).decode().strip().split()
        for pid in pids:
            os.kill(int(pid), signal.SIGTERM)
            print(f"Process {pid} has been stopped.")
    except subprocess.CalledProcessError:
        print("black_box/main.py is not currently running.")

def run_udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버가 시작되었습니다. 대기 중...")

    while True:
        data, address = sock.recvfrom(1024)
        message = data.decode().strip()
        print(f"수신된 메시지: {message} from {address}")

        if message == "0003":
            if not process_exists('black_box/main.py'):
                print("black_box/main.py 실행 중이 아닙니다. 프로세스를 시작합니다.")
                start_process()
            else:
                print("black_box/main.py 실행 중입니다. 프로세스를 종료합니다.")
                stop_process()

        raspberry_pi_ip = get_ip_address()
        if raspberry_pi_ip:
            response = f"{raspberry_pi_ip} 입니다"
            sock.sendto(response.encode(), address)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_udp_server)
    server_thread.start()
    server_thread.join()
