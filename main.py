import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time
import RPi.GPIO as GPIO

current_mode = 'manual'  # 자동 모드 강제 활성화를 위해 초기 모드 변경

# GPIO 핀 설정
def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    print(f"Initial GPIO 17 State: {GPIO.input(17)}")
    print(f"Initial GPIO 26 State: {GPIO.input(26)}")

# 상태 저장을 위한 딕셔너리
last_state = {
    17: GPIO.input(17),
    26: GPIO.input(26)
}

def check_gpio_changes(sock):
    global last_state
    while True:
        time.sleep(1)  # 상태 체크 주기
        for pin in last_state:
            current_state = GPIO.input(pin)
            if current_state != last_state[pin]:
                last_state[pin] = current_state
                message = f"GPIO {pin} {'HIGH' if current_state else 'LOW'}"
                print(f"Detected change on GPIO {pin}: {message}")  # 상태 변경 감지 로그 추가
                send_status(sock, "255.255.255.255", 12345, message)
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

def send_status(sock, ip, port, message):
    try:
        ip_address = get_ip_address()
        if ip_address:
            message_with_ip = f"IP:{ip_address} - {message}"
            print(f"Sending message: {message_with_ip}")  # 메시지 전송 로그 추가
            sock.sendto(message_with_ip.encode(), (ip, port))
        else:
            print("IP 주소를 가져오는 데 실패했습니다.")
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

def terminate_and_restart_blinker(mode_script, additional_args=""):
    try:
        # Terminate existing processes
        subprocess.call(['pkill', '-f', mode_script])
        print(f"{mode_script} 프로세스 종료됨.")
        # Start new process
        subprocess.Popen(['python3', mode_script] + additional_args.split())
        print(f"{mode_script} with {additional_args} 시작됨.")
    except Exception as e:
        print(f"{mode_script} 실행 중 오류 발생: {e}")

def enable_mode(mode):
    global current_mode
    print(f"현재 모드: {current_mode}, 요청 모드: {mode}")  # 현재 모드와 요청 모드 로깅
    script = 'led/gyro_led_steering.py'
    if mode == "manual" and current_mode != 'manual':
        terminate_and_restart_blinker(script, '--manual')
        current_mode = 'manual'
        print("수동 모드로 변경됨")
    elif mode == "auto" and current_mode != 'auto':
        terminate_and_restart_blinker(script, '--auto')
        current_mode = 'auto'
        print("자동 모드로 변경됨")

async def notify_status(websocket, path):
    last_status = None
    while True:
        await asyncio.sleep(1)
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        if recording_status != last_status:
            await websocket.send(recording_status)
            print(f"상태 업데이트 전송: {recording_status}")
            last_status = recording_status

def udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    global current_mode

    while True:
        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()

            if message == "Right Blinker Activated" and current_mode == 'manual':
                terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --right')
                send_status(sock, broadcast_ip, udp_port, "오른쪽 블링커 활성화됨")
            elif message == "Left Blinker Activated" and current_mode == 'manual':
                terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --left')
                send_status(sock, broadcast_ip, udp_port, "왼쪽 블링커 활성화됨")
            elif message == "REQUEST_IP":
                ip_address = get_ip_address()
                if ip_address:
                    send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
            elif message == "START_RECORDING":
                recording_status = start_recording()
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "STOP_RECORDING":
                recording_status = stop_recording()
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "REQUEST_RECORDING_STATUS":
                recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
                send_status(sock, broadcast_ip, udp_port, recording_status)
            elif message == "ENABLE_MANUAL_MODE":
                enable_mode("manual")
                send_status(sock, broadcast_ip, udp_port, "수동 모드 활성화됨")
            elif message == "ENABLE_AUTO_MODE":
                enable_mode("auto")
                send_status(sock, broadcast_ip, udp_port, "자동 모드 활성화됨")
        except socket.timeout:
            continue

def main():
    # 스크립트 시작 시 자동 모드 활성화 및 블랙박스 녹화 시작
    enable_mode("auto")  # 자동 모드 설정
    start_recording()  # 블랙박스 레코딩 시작

    loop = asyncio.get_event_loop()
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)

    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
