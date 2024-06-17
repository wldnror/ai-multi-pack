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
        # Connect to the device (replace this with the actual connection code)
        # socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        # socket.connect((target_address, 1))
        print("용준의 S24+")
    else:
        print("Could not find target bluetooth device nearby")

connect_bluetooth("용준의 S24+")
