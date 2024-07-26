import bluetooth
import subprocess
import threading
import re
import time
import RPi.GPIO as GPIO
from battery_monitor import read_battery_level

current_mode = 'manual'  # 초기 모드 설정

def get_ip_address():
    try:
        result = subprocess.check_output(["hostname", "-I"]).decode().strip()
        ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
        return ip_address
    except Exception as e:
        print(f"IP 주소 가져오기 실패: {e}")
        return None

def process_exists(process_name):
    try:
        process_list = subprocess.check_output(['ps', 'aux']).decode()
        if process_name in process_list:
            return True
        return False
    except Exception as e:
        print(f"프로세스 확인 중 오류 발생: {e}")
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    else:
        print("녹화 이미 진행 중.")
    return "RECORDING"

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("녹화 중지.")
        time.sleep(1)
        force_release_camera()
    except subprocess.CalledProcessError:
        print("녹화 프로세스를 찾을 수 없습니다.")
        force_release_camera()
    finally:
        return "NOT_RECORDING"

def force_release_camera():
    try:
        camera_process_output = subprocess.check_output(['fuser', '/dev/video0']).decode().strip()
        for pid in camera_process_output.split():
            subprocess.call(['kill', '-9', pid])
        print("카메라 자원 강제 해제.")
    except Exception as e:
        print(f"카메라 자원 해제 실패: {e}")

def terminate_and_restart_blinker(mode_script, additional_args=""):
    try:
        subprocess.call(['pkill', '-f', mode_script])
        print(f"{mode_script} 프로세스 종료됨.")
        subprocess.Popen(['python3', mode_script] + additional_args.split())
        print(f"{mode_script} 시작됨.")
    except Exception as e:
        print(f"{mode_script} 실행 중 오류 발생: {e}")

def enable_mode(mode):
    global current_mode
    print(f"현재 모드: {current_mode}, 요청 모드: {mode}")
    script = 'led/gyro_led_steering.py'
    if mode == "manual" and current_mode != 'manual':
        terminate_and_restart_blinker(script, '--manual')
        current_mode = 'manual'
        print("수동 모드로 변경됨")
    elif mode == "auto" and current_mode != 'auto':
        terminate_and_restart_blinker(script, '--auto')
        current_mode = 'auto'
        print("자동 모드로 변경됨")

def handle_client(client_sock):
    try:
        while True:
            data = client_sock.recv(1024).decode('utf-8')
            print(f"Data received: {data}")
            if data:
                if data == "Right Blinker Activated" and current_mode == 'manual':
                    terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --right')
                    client_sock.send("오른쪽 블링커 활성화됨".encode('utf-8'))
                elif data == "Left Blinker Activated" and current_mode == 'manual':
                    terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --left')
                    client_sock.send("왼쪽 블링커 활성화됨".encode('utf-8'))
                elif data == "REQUEST_IP":
                    ip_address = get_ip_address()
                    if ip_address:
                        client_sock.send(f"IP:{ip_address}".encode('utf-8'))
                elif data == "START_RECORDING":
                    recording_status = start_recording()
                    client_sock.send(recording_status.encode('utf-8'))
                elif data == "STOP_RECORDING":
                    recording_status = stop_recording()
                    client_sock.send(recording_status.encode('utf-8'))
                elif data == "REQUEST_RECORDING_STATUS":
                    recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
                    client_sock.send(recording_status.encode('utf-8'))
                elif data == "ENABLE_MANUAL_MODE":
                    enable_mode("manual")
                    client_sock.send("수동 모드 활성화됨".encode('utf-8'))
                elif data == "ENABLE_AUTO_MODE":
                    enable_mode("auto")
                    client_sock.send("자동 모드 활성화됨".encode('utf-8'))
            if not data:
                break
    except OSError as e:
        print(f"Connection error: {e}")
    finally:
        print("Disconnected")
        client_sock.close()

def bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", bluetooth.PORT_ANY))
    server_sock.listen(1)
    port = server_sock.getsockname()[1]
    print(f"Listening on port {port}")

    while True:
        print("Waiting for connection...")
        client_sock, client_info = server_sock.accept()
        print(f"Accepted connection from {client_info}")
        handle_client(client_sock)

def main():
    enable_mode("auto")
    start_recording()
    gpio_thread = threading.Thread(target=gpio_monitor, daemon=True)
    gpio_thread.start()
    
    # 블루투스 서버 시작
    bt_thread = threading.Thread(target=bluetooth_server, daemon=True)
    bt_thread.start()
    
    bt_thread.join()

if __name__ == "__main__":
    main()
