import bluetooth
import time

def connect_bluetooth(target_name):
    target_address = None
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)

    for addr, name in nearby_devices:
        if target_name == name:
            target_address = addr
            break

    if target_address is not None:
        print(f"Found target bluetooth device with address {target_address}")
        for port in range(1, 31):
            try:
                print(f"Trying port {port}")
                socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                socket.connect((target_address, port))
                print(f"Connected to port {port}")
                socket.send("Hello from Raspberry Pi!")
                socket.close()
                break
            except bluetooth.btcommon.BluetoothError as err:
                print(f"Port {port} failed: {err}")
                socket.close()
                time.sleep(1)
    else:
        print("Could not find target bluetooth device nearby")

connect_bluetooth("용준의 S24+")
