import bluetooth
import os
import subprocess
import uuid

# Ensure the Bluetooth adapter is up
subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'])

# Generate a UUID for your service
service_uuid = uuid.uuid4()

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
port = bluetooth.PORT_ANY
server_sock.bind(("", port))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# Advertise the service
try:
    bluetooth.advertise_service(server_sock, "BluetoothServer",
                                service_id=str(service_uuid),
                                service_classes=[str(service_uuid), bluetooth.SERIAL_PORT_CLASS],
                                profiles=[bluetooth.SERIAL_PORT_PROFILE])
    print(f"Waiting for connection on RFCOMM channel {port}, UUID: {service_uuid}")
except bluetooth.BluetoothError as e:
    print(f"Failed to advertise service: {e}")
    server_sock.close()
    exit(1)

try:
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")

    while True:
        data = client_sock.recv(1024)
        if not data:
            break
        print(f"Received: {data}")

except OSError:
    pass

print("Disconnected")

client_sock.close()
server_sock.close()
print("All done")
