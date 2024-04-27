import bluetooth
import time

def find_devices():
    print("검색 중...")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    return nearby_devices

def connect_to_device(addr):
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((addr, port))
        print(f"{addr}에 연결되었습니다.")
        return True
    except bluetooth.btcommon.BluetoothError as err:
        print(f"{addr}에 연결 실패: {err}")
        return False
    finally:
        sock.close()

def main():
    while True:
        connected_devices = bluetooth.discover_devices(duration=2, lookup_names=False)
        if not connected_devices:
            print("연결된 기기 없음. 주변 기기 검색 및 연결 시도.")
            devices = find_devices()
            for addr, name in devices:
                print(f"기기 발견: {name} [{addr}]")
                if connect_to_device(addr):
                    break
        else:
            print("이미 연결된 기기가 있습니다.")
        time.sleep(30)  # 30초마다 검사

if __name__ == "__main__":
    main()
