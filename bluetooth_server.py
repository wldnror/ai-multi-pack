import bluetooth
import time

# 핸드폰의 MAC 주소를 입력하세요
target_address = "BC:93:07:14:62:EE"

def connect_to_device(address):
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    try:
        sock.connect((address, 1))
        print(f"Connected to {address}")
        return sock
    except bluetooth.btcommon.BluetoothError as err:
        print(f"Connection to {address} failed: {err}")
        return None

def main():
    while True:
        print("Attempting to connect...")
        sock = connect_to_device(target_address)
        if sock:
            try:
                while True:
                    data = sock.recv(1024)
                    if data:
                        print(f"Received: {data}")
            except bluetooth.btcommon.BluetoothError as err:
                print(f"Connection lost: {err}")
                sock.close()
        print("Reconnecting in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    main()
