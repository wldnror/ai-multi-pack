import socket

def run_udp_server():
    # 로컬 IP 주소와 포트를 설정합니다.
    local_ip = "0.0.0.0"
    local_port = 5005
    buffer_size = 1024

    # UDP 소켓을 생성합니다.
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # 소켓을 로컬 주소와 포트에 바인드합니다.
    server_socket.bind((local_ip, local_port))

    print("UDP server up and listening")

    # 메시지를 수신 대기합니다.
    while True:
        bytes_address_pair = server_socket.recvfrom(buffer_size)
        message = bytes_address_pair[0]
        address = bytes_address_pair[1]

        client_msg = "Message from Client:{}".format(message)
        client_ip = "Client IP Address:{}".format(address)
        
        print(client_msg)
        print(client_ip)

        # 클라이언트에게 응답을 보냅니다.
        server_socket.sendto(str.encode("Hello UDP Client"), address)

if __name__ == '__main__':
    run_udp_server()
