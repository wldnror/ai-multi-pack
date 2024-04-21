import subprocess
import time
import json
import os

profile_info_file = "successful_profiles.json"

def save_successful_profiles(device_address, profiles):
    # 성공적으로 연결된 프로파일을 파일에 저장
    with open(profile_info_file, 'w') as file:
        json.dump({device_address: profiles}, file)

def load_successful_profiles(device_address):
    # 파일에서 프로파일 정보 로드
    if os.path.exists(profile_info_file):
        with open(profile_info_file, 'r') as file:
            data = json.load(file)
            return data.get(device_address, [])
    return []

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

def is_device_connected(device_address):
    # 블루투스 장치의 연결 상태 확인
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    if "Connected: yes" in result.stdout:
        return True
    return False

def connect_bluetooth_device(device_address):
    # 저장된 프로파일 정보를 사용하여 장치에 연결
    profiles = load_successful_profiles(device_address)
    if not profiles:
        print("No saved profile information found for automatic connection.")
        return False

    print(f"Connecting to {device_address} using saved profiles...")
    for profile in profiles:
        if is_device_connected(device_address):
            print(f"Device {device_address} is already connected.")
            return True
        try:
            print(f"Attempting to connect profile {profile}...")
            result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
            if "Connection successful" in result.stdout:
                print("Connected to the device successfully.")
                return True
            else:
                print(f"Connection failed. Retrying...\nstdout: {result.stdout}\nstderr: {result.stderr}")
                time.sleep(10)
        except Exception as e:
            print(f"Error connecting to the device: {str(e)}")
            time.sleep(10)
    return False

if __name__ == '__main__':
    device_address = get_last_connected_device()
    if device_address:
        print(f"Attempting to connect to the last connected device: {device_address}")
        if not connect_bluetooth_device(device_address):
            print("Failed to connect using saved profiles.")
    else:
        print("No paired devices found.")
