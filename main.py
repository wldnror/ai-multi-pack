import asyncio
import websockets
import socket
import subprocess
import threading
import re
import time
import RPi.GPIO as GPIO
from battery_monitor import read_battery_level

current_mode = 'manual'  # 초기 모드 설정
connected_clients = set()  # 클라이언트 세션 저장을 위한 집합

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
            sock.sendto(message_with_ip.encode(), (ip, port))
        else:
            print("IP 주소를 가져오는 데 실패했습니다.")
    except Exception as e:
        print(f"메시지 전송 실패: {e}")

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

async def notify_status(websocket, path):
    global connected_clients
    connected_clients.add(websocket)
    try:
        last_status = None
        while True:
            await asyncio.sleep(1)
            recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
            if recording_status != last_status:
                await websocket.send(recording_status)
                print(f"상태 업데이트 전송: {recording_status}")
                last_status = recording_status

            # 배터리 잔량 읽어오기
            voltage, current, power, battery_percentage = read_battery_level()
            battery_status = f"Battery - Voltage: {voltage:.2f}V, Current: {current:.2f}mA, Power: {power:.2f}mW, Level: {battery_percentage:.2f}%"
            await websocket.send(battery_status)
            print(f"배터리 상태 전송: {battery_status}")

    finally:
        connected_clients.remove(websocket)

def gpio_monitor():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    pins = [17, 26]
    for pin in pins:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def pin_callback(channel):
        state = GPIO.input(channel)
        message = f"Pin {channel} is {'on' if state else 'off'}"
        print(message)
        asyncio.run_coroutine_threadsafe(
            broadcast_message(message), asyncio.get_event_loop()
        )

    for pin in pins:
        try:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=pin_callback, bouncetime=200)
        except RuntimeError as e:
            print(f"Error setting up GPIO detection on pin {pin}: {e}")

    try:
        # Add MPU6050 initialization code here
        import smbus
        MPU6050_ADDR = 0x69

        def MPU6050_init():
            bus = smbus.SMBus(1)
            bus.write_byte_data(MPU6050_ADDR, 0x6B, 0x00)  # Wake up the MPU6050
            print("MPU6050 센서 초기화 완료.")

        MPU6050_init()
    except Exception as e:
        print(f"MPU6050 센서 초기화 실패: {e}")
        pass

async def broadcast_message(message):
    global connected_clients
    for client in connected_clients:
        await client.send(message)
        print(f"메시지 전송됨: {message}")

def ip_broadcast(sock, broadcast_ip, udp_port):
    while True:
        try:
            ip_address = get_ip_address()
            if ip_address:
                send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
            time.sleep(0.5)  # 1초마다 IP 전송
        except Exception as e:
            print(f"IP 전송 오류: {e}")

def udp_server():
    udp_ip = "0.0.0.0"
    udp_port = 12345
    broadcast_ip = "255.255.255.255"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((udp_ip, udp_port))
    print("UDP 서버 시작됨. 대기중...")

    global current_mode

    def handle_message(data, addr):
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
                send_status(sock, broadcast_ip, udp_port)
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

    while True:
        try:
            sock.settimeout(0.1)
            data, addr = sock.recvfrom(1024)
            handle_message(data, addr)
        except socket.timeout:
            continue
    return sock

def main():
    enable_mode("auto")
    start_recording()
    loop = asyncio.get_event_loop()
    gpio_thread = threading.Thread(target=gpio_monitor, daemon=True)
    gpio_thread.start()
    sock = udp_server()
    udp_thread = threading.Thread(target=udp_server, daemon=True)
    udp_thread.start()
    
    # IP 정보를 1초마다 전송하는 스레드 시작
    ip_thread = threading.Thread(target=ip_broadcast, args=(sock, "255.255.255.255", 12345), daemon=True)
    ip_thread.start()
    
    websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
    loop.run_until_complete(websocket_server)
    loop.run_forever()

if __name__ == "__main__":
    main()
