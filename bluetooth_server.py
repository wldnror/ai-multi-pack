import bluetooth

# 서비스 이름 및 UUID 설정
service_name = "YongGulRiderService"
service_uuid = "00001101-0000-1000-8000-00805F9B34FB"

# 블루투스 서버 소켓 생성
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

# 포트 번호 가져오기
port = server_sock.getsockname()[1]

try:
    # 서비스 광고 시작
    bluetooth.advertise_service(
        server_sock, service_name,
        service_id=service_uuid,
        service_classes=[service_uuid, bluetooth.SERIAL_PORT_CLASS],
        profiles=[bluetooth.SERIAL_PORT_PROFILE]
    )
    print(f"Bluetooth service '{service_name}' started on port {port}")

    while True:
        print("Waiting for connection...")
        client_sock, client_info = server_sock.accept()
        print(f"Accepted connection from {client_info}")

        try:
            while True:
                data = client_sock.recv(1024)
                if not data:
                    break
                print(f"Received: {data}")
                client_sock.send(data)
        except OSError:
            pass

        print("Connection closed")
        client_sock.close()
except bluetooth.btcommon.BluetoothError as e:
    print(f"Bluetooth error occurred: {e}")
finally:
    print("Shutting down server...")
    server_sock.close()
