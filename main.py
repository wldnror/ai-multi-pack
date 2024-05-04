import asyncio
import websockets
import subprocess
import re
import time

async def notify_status(websocket, path):
    while True:
        await asyncio.sleep(1)  # 상태를 1초마다 확인
        recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
        await websocket.send(recording_status)  # 상태를 WebSocket을 통해 전송

async def main():
    async with websockets.serve(notify_status, "0.0.0.0", 8765):
        await asyncio.Future()  # 서버가 계속 실행되도록 함

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
        subprocess.check_output(['pgrep', '-f', process_name])
        return True
    except subprocess.CalledProcessError:
        return False

def start_recording():
    if not process_exists('black_box/main.py'):
        subprocess.Popen(['python3', 'black_box/main.py'])
        print("녹화 시작.")
    return "RECORDING"

def stop_recording():
    try:
        subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
        print("Recording stopped.")
        time.sleep(1)
        force_release_camera()
    except subprocess.CalledProcessError:
        print("Recording process not found.")
        force_release_camera()
    return "NOT_RECORDING"

def force_release_camera():
    try:
        camera_process_output = subprocess.check_output(['fuser', '/dev/video0']).decode().strip()
        for pid in camera_process_output.split():
            subprocess.call(['kill', '-9', pid])
        print("Camera resource forcefully released.")
    except Exception as e:
        print(f"Failed to release camera resource: {e}")

if __name__ == "__main__":
    asyncio.run(main())
