import socket
import subprocess
import re
import multiprocessing
import serve1

def get_ip_address():
    try:
        결과 = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        ip_주소들 = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', 결과)
        return ip_주소들[0] if ip_주소들 else None
    except subprocess.CalledProcessError:
        return None

def handle_client(client_conn, udp_socket):
    while True:
        데이터, 주소 = udp_socket.recvfrom(1024)
        print(f"수신된 메시지: {데이터.decode()} from {주소}")

        # 메시지에 따라 내부 프로세스(serve1)로 메시지를 전송
        if 데이터.decode() == "button1":
            client_conn.send("activate serve1")

        # 외부(안드로이드 앱)로 응답
        라즈베리파이_ip = get_ip_address()
        if 데이터 and 라즈베리파이_ip:
            응답 = f"내 IP 주소는 {라즈베리파이_ip}입니다"
            udp_socket.sendto(응답.encode(), 주소)

if __name__ == "__main__":
    # UDP 설정
    udp_ip = "0.0.0.0"
    udp_port = 12345
    소켓 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    소켓.bind((udp_ip, udp_port))
    print("UDP 서버가 시작되었습니다. 대기 중...")

    # 파이프 생성
    parent_conn, child_conn = multiprocessing.Pipe()

    # serve1 프로세스 생성 및 실행
    serve1_process = multiprocessing.Process(target=serve1.run, args=(child_conn,))
    serve1_process.start()

    # 클라이언트 핸들링
    handle_client(parent_conn, 소켓)

    # 종료 후 정리
    serve1_process.join()
    소켓.close()
