import asyncio
import websockets
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
        print(f"IP 주소 가져오기 실패: {e}")
        return None

def process_exists(process_name):
    try:
        process_list = subprocess.check_output(['ps', 'aux']).decode()
        for process in process_list.splitlines():
            if process_name in process:
                return True
        return False
    except Exception as e:
        print(f"프로세스 확인 중 오류 발생: {e}")
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
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
            sock.sendto(message_with_ip.encode(), (ip, port))
        else:
            print("IP 주소를 가져오는 데 실패했습니다.")
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

def terminate_mode_process(mode_script):
    try:
        output = subprocess.check_output(['pgrep', '-f', mode_script]).decode().strip()
        if output:
            pids = output.split()
            for pid in pids:
                subprocess.call(['kill', '-9', pid])
            print(f"{mode_script} 프로세스 종료됨.")
    except subprocess.CalledProcessError:
        print(f"{mode_script} 프로세스를 찾을 수 없습니다.")
    except Exception as e:
        print(f"프로세스 종료 중 오류 발생: {e}")

def enable_mode(mode):
    if mode == "manual":
        terminate_mode_process('led/gyro_led_steering.py --auto')
        subprocess.Popen(['python3', 'led/gyro_led_steering.py', '--manual'])
        print("수동 모드 활성화됨")
    elif mode == "auto":
        terminate_mode_process('led/gyro_led_steering.py --manual')
        subprocess.Popen(['python3', 'led/gyro_led_steering.py', '--auto'])
        print("자동 모드 활성화됨")

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

    while True:
        try:
            sock.settimeout(1)
            data, addr = sock.recvfrom(1024)
            message = data.decode().strip()
            # print(f"수신된 메시지: {message} from {addr}")

            if message == "REQUEST_IP":
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
            elif message == "Right Blinker Activated":
                print("오른쪽 블링커 활성화됨")
                subprocess.Popen(['python3', 'led/gyro_led_steering.py', '--manual', '--right'])
                send_status(sock, broadcast_ip, udp_port, "오른쪽 블링커 활성화됨")
            elif message == "Left Blinker Activated":
                print("왼쪽 블링커 활성화됨")
                subprocess.Popen(['python3', 'led/gyro_led_steering.py', '--manual', '--left'])
                send_status(sock, broadcast_ip, udp_port, "왼쪽 블링커 활성화됨")
            elif message == "ENABLE_MANUAL_MODE":
                enable_mode("manual")
                send_status(sock, broadcast_ip, udp_port, "수동 모드 활성화됨")
            elif message == "ENABLE_AUTO_MODE":
                enable_mode("auto")
                send_status(sock, broadcast_ip, udp_port, "자동 모드 활성화됨")
        except socket.timeout:
            continue

def main():
    loop = asyncio.get_event_loop()
    udp_thread = threading.Thread(target=udp_server)
    udp_thread.start()
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
