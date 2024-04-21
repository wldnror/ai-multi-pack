import subprocess
import time

def check_device_connected(device_address):
    # 특정 장치의 연결 상태를 확인
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    return "Connected: yes" in result.stdout

def get_last_connected_device():
    # 가장 최근에 연결된 블루투스 장치의 MAC 주소를 가져옴
    result = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    for line in reversed(lines):
        if "Device" in line:
            parts = line.split()
            if len(parts) >= 2:
                return parts[1]
    return None

def connect_bluetooth_device(device_address):
    # 블루투스 장치 연결 시도
    if check_device_connected(device_address):
        print("A device is already connected.")
        return
    while True:
        result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
        if "Connection successful" in result.stdout:
            if check_device_connected(device_address):
                print("Connected to the device successfully.")
                break
            else:
                print("Connection failed. Retrying...")
        else:
            print(f"Connection failed: {result.stderr.strip()}")
        time.sleep(10)

if __name__ == '__main__':
    device_address = get_last_connected_device()
    if device_address:
        print(f"Attempting to connect to the last connected device: {device_address}")
        connect_bluetooth_device(device_address)
    else:
        print("No paired devices found.")
