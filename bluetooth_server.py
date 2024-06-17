import subprocess
import time

def bluetoothctl_command(command):
    process = subprocess.Popen(['bluetoothctl'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate(command.encode('utf-8'))
    return output.decode('utf-8'), error.decode('utf-8')

def is_device_connected(mac_address):
    output, error = bluetoothctl_command(f'info {mac_address}\n')
    return 'Connected: yes' in output

def connect_bluetooth_device(mac_address):
    commands = [
        'power on\n',
        'agent on\n',
        'default-agent\n',
        f'connect {mac_address}\n'
    ]

    for command in commands:
        print(f"Running command: {command.strip()}")
        output, error = bluetoothctl_command(command)
        print(output)
        if error:
            print(f"Error: {error}")

    # Check if the device is connected
    if is_device_connected(mac_address):
        print(f"Successfully connected to {mac_address}")
    else:
        print(f"Failed to connect to {mac_address}")

def main():
    mac_address = "BC:93:07:14:62:EE"  # Replace with your device's MAC address
    while True:
        if not is_device_connected(mac_address):
            print("Device not connected. Attempting to connect...")
            connect_bluetooth_device(mac_address)
        else:
            print("Device is already connected.")
        
        time.sleep(60)  # Check connection status every 60 seconds

if __name__ == "__main__":
    main()
