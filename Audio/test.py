import bluetooth
import subprocess
import time

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
    device_address = 'BC:93:07:14:62:EE'  # 대상 블루투스 장치의 MAC 주소
    connect_bluetooth_device(device_address)
