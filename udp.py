import socket
import subprocess
import re
import multiprocessing

def get_ip_address():
    try:
        결과 = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_주소들 = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 결과)
        return ip_주소들[0] if ip_주소들 else None
    except subprocess.CalledProcessError:
        return None

def handle_client(udp_socket, conn_dict):
    while True:
        데이터, 주소 = udp_socket.recvfrom(1024)
        print(f"수신된 메시지: {데이터.decode()} from {주소}")

        message = 데이터.decode()
        if message.startswith("button"):
            button_number = int(message[-1])  # 'button1'이면 1을 추출
            if button_number in conn_dict:
                conn_dict[button_number].send(message)  # 해당 버튼 번호에 맞는 프로세스에 메시지 전송

        라즈베리파이_ip = get_ip_address()
        if 데이터 and 라즈베리파이_ip:
            응답 = f"내 IP 주소는 {라즈베리파이_ip}입니다"
            udp_socket.sendto(응답.encode(), 주소)

if __name__ == "__main__":
    udp_ip = "0.0.0.0"
    udp_port = 12345
    소켓 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    소켓.bind((udp_ip, udp_port))
    print("UDP 서버가 시작되었습니다. 대기 중...")

    # 프로세스 및 파이프 생성
    conn_dict = {}
    processes = []
    for i in range(1, 4):  # 예시로 3개의 서브 스크립트를 사용
        parent_conn, child_conn = multiprocessing.Pipe()
        p = multiprocessing.Process(target=eval(f'serve{i}.run'), args=(child_conn,))
        p.start()
        processes.append(p)
        conn_dict[i] = parent_conn  # 버튼 번호와 연결

    handle_client(소켓, conn_dict)

    for p in processes:
        p.join()
    소켓.close()
