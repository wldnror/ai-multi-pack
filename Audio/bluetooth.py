import subprocess
import json
import os

profile_info_file = "bluetooth_profiles.json"

def save_profile_info(device_address, profiles):
    with open(profile_info_file, 'w') as file:
        json.dump({device_address: profiles}, file)

def load_profile_info(device_address):
    if os.path.exists(profile_info_file):
        with open(profile_info_file, 'r') as file:
            data = json.load(file)
            return data.get(device_address, [])
    return []

def get_connected_device_profiles(device_address):
    # bluetoothctl을 사용하여 장치의 프로파일을 조회
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    profiles = []
    for line in result.stdout.splitlines():
        if "UUID:" in line:
            uuid = line.split()[-1].strip('()')
            profiles.append(uuid)
    return profiles

def connect_bluetooth_device(device_address):
    profiles = load_profile_info(device_address)
    if not profiles:
        print("No profile information found. Fetching profiles...")
        profiles = get_connected_device_profiles(device_address)
        save_profile_info(device_address, profiles)

    print(f"Attempting to connect to {device_address} with saved profiles...")
    result = subprocess.run(['bluetoothctl', 'connect', device_address], capture_output=True, text=True)
    if "Connection successful" in result.stdout:
        print("Connected successfully. Restoring profiles...")
        for profile in profiles:
            print(f"Setting up {profile}...")
            # 프로파일 복구 작업 추가
    else:
        print(f"Failed to connect: {result.stderr}")

if __name__ == '__main__':
    device_address = 'BC:93:07:14:62:EE'  # 예시 MAC 주소
    connect_bluetooth_device(device_address)
