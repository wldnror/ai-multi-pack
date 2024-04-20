import subprocess
import time

def any_device_connected():
    # bluetoothctl을 사용하여 모든 연결된 장치를 확인
    process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    process.stdin.write('info\n')
    process.stdin.write('exit\n')
    out, err = process.communicate()
    if "Connected: yes" in out:
        return True
    return False

def get_last_connected_device():
    # bluetoothctl을 통해 페어링된 장치 목록을 가져옴
    process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    process.stdin.write('devices\n')
    process.stdin.write('exit\n')
    out, err = process.communicate()
    if out:
        lines = out.strip().split('\n')
        for line in reversed(lines):
            if "Device" in line:
                parts = line.split()
                if len(parts) >= 2:
                    mac_address = parts[1]  # MAC 주소 추출
                    return mac_address
    return None

def connect_bluetooth_device(device_address):
    # 블루투스 장치 연결 시도 전에 전체 연결 상태 확인
    if any_device_connected():
        print("A device is already connected.")
        return
    while True:  # 무한 반복
        try:
            result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
            if "Connection successful" in result.stdout:
                print("Connected to the device successfully.")
                break
            else:
                print("Connection failed. Retrying...")
                time.sleep(10)  # 10초 후 재시도
        except Exception as e:
            print(f"Error connecting to the device: {str(e)}")
            time.sleep(10)  # 예외 발생시에도 10초 후 재시도

if __name__ == '__main__':
    if not any_device_connected():  # 장치 연결 상태 먼저 확인
        device_address = get_last_connected_device()
        if device_address:
            print(f"Attempting to connect to the last connected device: {device_address}")
            connect_bluetooth_device(device_address)
        else:
            print("No paired devices found.")
    else:
        print("A device is already connected, no need to reconnect.")
