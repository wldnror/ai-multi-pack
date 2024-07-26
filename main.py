import asyncio
import subprocess
import re

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

async def handle_client(reader, writer):
    try:
        print("클라이언트 연결됨")
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode('utf-8').strip()
            print(f"Received: {message}")
            
            if message == "Right Blinker Activated":
                terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --right')
                response = "오른쪽 깜박이 활성화됨"
            elif message == "Left Blinker Activated":
                terminate_and_restart_blinker('led/gyro_led_steering.py', '--manual --left')
                response = "왼쪽 깜박이 활성화됨"
            elif message == "REQUEST_IP":
                ip_address = get_ip_address()
                response = f"IP:{ip_address}" if ip_address else "IP 주소를 가져올 수 없습니다"
            elif message == "START_RECORDING":
                response = start_recording()
            elif message == "STOP_RECORDING":
                response = stop_recording()
            elif message == "REQUEST_RECORDING_STATUS":
                response = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
            elif message == "ENABLE_MANUAL_MODE":
                enable_mode("manual")
                response = "수동 모드 활성화됨"
            elif message == "ENABLE_AUTO_MODE":
                enable_mode("auto")
                response = "자동 모드 활성화됨"
            else:
                response = "알 수 없는 명령"
            
            writer.write(response.encode('utf-8'))
            await writer.drain()
    except Exception as e:
        print(f"Client handling error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 12345)
    print("서버 시작됨")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
