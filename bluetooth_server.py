import bluetooth

def connect_bluetooth(target_name):
    target_address = None
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)

    for addr, name in nearby_devices:
        if target_name == name:
            target_address = addr
            break

    if target_address is not None:
        print(f"Found target bluetooth device with address {target_address}")
        try:
            # Create a Bluetooth socket and connect to the target address
            port = 1  # 포트는 필요에 따라 조정
            socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            print("Creating socket...")
            socket.connect((target_address, port))
            print("Connected to the device")

            # Optionally, you can send some data to the connected device
            socket.send("Hello from Raspberry Pi!")
            socket.close()
        except bluetooth.btcommon.BluetoothError as err:
            print(f"Failed to connect to the device: {err}")
            # 포트 번호를 변경해 보거나 다른 방법을 시도
            for p in range(1, 31):
                try:
                    print(f"Trying port {p}")
                    socket.connect((target_address, p))
                    print(f"Connected to port {p}")
                    socket.send("Hello from Raspberry Pi!")
                    socket.close()
                    break
                except bluetooth.btcommon.BluetoothError as inner_err:
                    print(f"Port {p} failed: {inner_err}")
    else:
        print("Could not find target bluetooth device nearby")

connect_bluetooth("용준의 S24+")
