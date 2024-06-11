import bluetooth

# UUID 설정
uuid = "00001101-0000-1000-8000-00805F9B34FB"  # SPP (Serial Port Profile) UUID

# 블루투스 서버 소켓 생성
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

# 서비스 광고 설정
bluetooth.advertise_service(server_sock, "BluetoothServer",
                            service_id=uuid,
                            service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                            profiles=[bluetooth.SERIAL_PORT_PROFILE])

print(f"Waiting for connection on RFCOMM channel {port}")

# 클라이언트 연결 수락
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
