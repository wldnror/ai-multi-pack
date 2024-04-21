import subprocess
import time
import json
import os

profile_info_file = "successful_profiles.json"

def save_successful_profiles(device_address, profiles):
    # 성공적으로 연결된 프로파일을 파일에 저장
    data = {}
    if os.path.exists(profile_info_file):
        with open(profile_info_file, 'r') as file:
            data = json.load(file)
    data[device_address] = profiles
    with open(profile_info_file, 'w') as file:
        json.dump(data, file, indent=4)

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
    return "Connected: yes" in result.stdout

def get_connected_device_profiles(device_address):
    # 연결된 장치의 프로파일 정보 가져오기
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    profiles = []
    if "UUID" in result.stdout:
        lines = result.stdout.split('\n')
        for line in lines:
            if "UUID" in line:
                uuid = line.split()[-1].strip()
                profiles.append(uuid)
    return profiles

def connect_bluetooth_device(device_address):
    # 블루투스 장치 연결 시도
    if is_device_connected(device_address):
        print(f"Device {device_address} is already connected.")
        profiles = get_connected_device_profiles(device_address)
        save_successful_profiles(device_address, profiles)
        return
    
    while True:
        try:
            result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
            if "Connection successful" in result.stdout:
                print("Connected to the device successfully.")
                profiles = get_connected_device_profiles(device_address)
                save_successful_profiles(device_address, profiles)
                break
            else:
                print(f"Connection failed. Retrying...\nstdout: {result.stdout}\nstderr: {result.stderr}")
                time.sleep(10)  # 10초 후 재시도
        except Exception as e:
            print(f"Error connecting to the device: {str(e)}")
            time.sleep(10)

if __name__ == '__main__':
    device_address = get_last_connected_device()
    if device_address:
        print(f"Attempting to connect to the last connected device: {device_address}")
        connect_bluetooth_device(device_address)
    else:
        print("No paired devices found.")
