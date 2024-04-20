import subprocess
import time

def get_last_connected_device():
    # bluetoothctl을 통해 페어링된 장치 목록을 가져옴
    result = subprocess.run(['bluetoothctl', 'paired-devices'], capture_output=True, text=True)
    if result.stdout:
        devices = result.stdout.strip().split('\n')
        for device in reversed(devices):  # 가장 최근에 연결된 장치를 찾기 위해 역순으로 검색
            parts = device.split()
            if len(parts) >= 2:
                mac_address = parts[1]
                return mac_address
    return None

def connect_bluetooth_device(device_address):
    # 블루투스 장치 연결 시도
    while True:
        try:
            result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
            if "Connection successful" in result.stdout:
                print("Connected to the device successfully.")
                break
            else:
                print("Connection failed. Retrying...")
                time.sleep(5)  # 5초 후 재시도
        except Exception as e:
            print(f"Error connecting to the device: {str(e)}")
            time.sleep(5)

if __name__ == '__main__':
    device_address = get_last_connected_device()
    if device_address:
        print(f"Attempting to connect to the last connected device: {device_address}")
        connect_bluetooth_device(device_address)
    else:
        print("No paired devices found.")
