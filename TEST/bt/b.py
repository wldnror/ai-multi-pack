import bluetooth
import uuid

# 블루투스 소켓 생성 및 바인드
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# UUID 생성
service_uuid = str(uuid.uuid4())
print(f"Generated UUID: {service_uuid}")

# 블루투스 서비스 광고
bluetooth.advertise_service(server_sock, "BluetoothServer",
                            service_id=service_uuid,
                            service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print(f"Waiting for connection on RFCOMM channel {port}")

client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

try:
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
