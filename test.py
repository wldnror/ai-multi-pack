import bluetooth
import time

target_name = "용굴라이더"  # 연결할 장치의 이름
target_address = None

def find_device(target_name):
    nearby_devices = bluetooth.discover_devices(lookup_names=True)
    for addr, name in nearby_devices:
        if target_name == name:
            return addr
    return None

while True:
    print("Searching for target device...")
    target_address = find_device(target_name)

    if target_address is not None:
        print(f"Found target device with address {target_address}")
        break
    else:
        print("Could not find target device. Retrying...")
    time.sleep(5)  # 5초마다 다시 검색

# 연결 시도
if target_address:
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_address, port))
    print(f"Connected to {target_name} with address {target_address}")
    
    # 이후 소켓을 통해 데이터 전송 등 필요한 작업 수행
    # ...

    sock.close()
