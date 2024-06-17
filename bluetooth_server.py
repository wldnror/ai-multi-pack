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
            socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            socket.connect((target_address, 1))
            print("Connected to the device")

            # Optionally, you can send some data to the connected device
            socket.send("Hello from Raspberry Pi!")
            socket.close()
        except bluetooth.btcommon.BluetoothError as err:
            print(f"Failed to connect to the device: {err}")
    else:
        print("Could not find target bluetooth device nearby")

connect_bluetooth("용준의 S24+")
