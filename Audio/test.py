import subprocess
import time
import json
import os

profile_info_file = "successful_profiles.json"

def save_successful_profiles(device_address, profiles):
    data = {}
    if os.path.exists(profile_info_file):
        with open(profile_info_file, 'r') as file:
            data = json.load(file)
    data[device_address] = profiles
    with open(profile_info_file, 'w') as file:
        json.dump(data, file, indent=4)

def load_successful_profiles(device_address):
    if os.path.exists(profile_info_file):
        with open(profile_info_file, 'r') as file:
            data = json.load(file)
            return data.get(device_address, [])
    return []

def get_last_connected_device():
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
                    mac_address = parts[1]
                    return mac_address
    return None

def is_device_connected(device_address):
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    if "Connected: yes" in result.stdout:
        return True
    return False

def get_connected_device_profiles(device_address):
    result = subprocess.run(['bluetoothctl', 'info', device_address], capture_output=True, text=True)
    profiles = []
    if "UUID" in result.stdout:
        lines = result.stdout.split('\n')
        for line in lines:
            if "UUID" in line:
                uuid = line.split()[-1].strip()
                profiles.append(uuid)
    return profiles

def verify_active_connection(device_address):
    # 예를 들어, `pactl`을 사용하여 오디오 스트림이 활성화되었는지 확인
    result = subprocess.run(['pactl', 'list', 'sinks'], capture_output=True, text=True)
    return "RUNNING" in result.stdout

def connect_bluetooth_device(device_address):
    connected = is_device_connected(device_address)
    if connected:
        if verify_active_connection(device_address):
            print(f"Device {device_address} is actively connected.")
        else:
            print(f"Device {device_address} seems connected but not actively transmitting.")
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
                time.sleep(10)
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
