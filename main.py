# import asyncio
# import websockets
# import socket
# import subprocess
# import threading
# import re
# import time

# def get_ip_address():
#     try:
#         result = subprocess.check_output(["hostname", "-I"]).decode().strip()
#         ip_address = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', result)[0]
#         return ip_address
#     except Exception as e:
#         print(f"IP 주소 가져오기 실패: {e}")
#         return None

# def process_exists(process_name):
#     try:
#         process_list = subprocess.check_output(['ps', 'aux']).decode()
#         for process in process_list.splitlines():
#             if process_name in process:
#                 return True
#         return False
#     except Exception as e:
#         print(f"Error checking processes: {e}")
#         return False

# def start_recording():
#     if not process_exists('black_box/main.py'):
#         subprocess.Popen(['python3', 'black_box/main.py'])
#         print("녹화 시작.")
#     return "RECORDING"

# def stop_recording():
#     try:
#         subprocess.check_output(['pkill', '-f', 'black_box/main.py'])
#         print("Recording stopped.")
#         time.sleep(1)  # 프로세스 종료를 기다림
#         force_release_camera()  # 카메라 자원 해제 시도
#     except subprocess.CalledProcessError:
#         print("Recording process not found.")
#         force_release_camera()
#     finally:
#         return "NOT_RECORDING"

# def force_release_camera():
#     try:
#         camera_process_output = subprocess.check_output(['fuser', '/dev/video0']).decode().strip()
#         for pid in camera_process_output.split():
#             subprocess.call(['kill', '-9', pid])
#         print("Camera resource forcefully released.")
#     except Exception as e:
#         print(f"Failed to release camera resource: {e}")

# def send_status(sock, ip, port, message):
#     try:
#         ip_address = get_ip_address()
#         if ip_address:
#             message_with_ip = f"IP:{ip_address} - {message}"
#             sock.sendto(message_with_ip.encode(), (ip, port))
#             print(f"Sent message with IP: {message_with_ip} to {ip}:{port}")
#         else:
#             print("Failed to get IP address.")
#     except Exception as e:
#         print(f"Failed to send message: {e}")

# async def notify_status(websocket, path):
#     last_status = None
#     while True:
#         await asyncio.sleep(1)  # 상태를 확인하는 간격을 1초로 설정
#         recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
#         if recording_status != last_status:
#             await websocket.send(recording_status)
#             print(f"상태 업데이트 전송: {recording_status}")
#             last_status = recording_status

# def udp_server():
#     udp_ip = "0.0.0.0"
#     udp_port = 12345
#     broadcast_ip = "255.255.255.255"
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#     sock.bind((udp_ip, udp_port))
#     print("UDP 서버 시작됨. 대기중...")

#     while True:
#         try:
#             sock.settimeout(1)
#             data, addr = sock.recvfrom(1024)
#             message = data.decode().strip()
#             print(f"메시지 수신됨: {message} from {addr}")

#             if message == "REQUEST_IP":
#                 ip_address = get_ip_address()
#                 if ip_address:
#                     send_status(sock, broadcast_ip, udp_port, f"IP:{ip_address}")
#             elif message == "START_RECORDING":
#                 recording_status = start_recording()
#                 send_status(sock, broadcast_ip, udp_port, recording_status)
#             elif message == "STOP_RECORDING":
#                 recording_status = stop_recording()
#                 send_status(sock, broadcast_ip, udp_port, recording_status)
#             elif message == "REQUEST_RECORDING_STATUS":
#                 recording_status = "RECORDING" if process_exists('black_box/main.py') else "NOT_RECORDING"
#                 send_status(sock, broadcast_ip, udp_port, recording_status)
#             elif message == "Right Blinker Activated":
#                 print("오른쪽 블링커 활성화됨")
#                 subprocess.call(['python3', 'led/gyro_led_steering.py', 'right_on'])
#                 send_status(sock, broadcast_ip, udp_port, "오른쪽 블링커 활성화됨")
#             elif message == "Left Blinker Activated":
#                 print("왼쪽 블링커 활성화됨")
#                 subprocess.call(['python3', 'led/gyro_led_steering.py', 'left_on'])
#                 send_status(sock, broadcast_ip, udp_port, "왼쪽 블링커 활성화됨")

#         except socket.timeout:
#             continue

# def main():
#     loop = asyncio.get_event_loop()
#     udp_thread = threading.Thread(target=udp_server)
#     udp_thread.start()
#     websocket_server = websockets.serve(notify_status, "0.0.0.0", 8765)
#     loop.run_until_complete(websocket_server)
#     loop.run_forever()

# if __name__ == "__main__":
#     main()


import socket
import time

def request_ip_and_send_messages():
    server_ip = "0.0.0.0"  # 서버 IP 주소
    server_port = 12345  # 서버 포트
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 서버에게 IP 주소 요청
    sock.sendto("REQUEST_IP".encode(), (server_ip, server_port))
    try:
        sock.settimeout(5)
        data, addr = sock.recvfrom(1024)  # 서버로부터 응답 수신
        my_ip = data.decode()
        print(f"서버로부터 받은 IP 주소: {my_ip}")
    except socket.timeout:
        print("서버로부터 응답이 없습니다.")
        return

    messages = [
        "START_RECORDING", "STOP_RECORDING",
        "REQUEST_RECORDING_STATUS", "Right Blinker Activated",
        "Left Blinker Activated"
    ]

    while True:
        print("\n메시지 목록:")
        for idx, msg in enumerate(messages):
            print(f"{idx + 1}: {msg}")
        choice = input("메시지 번호를 선택하세요 (종료하려면 'q'를 입력): ")
        if choice.lower() == 'q':
            print("클라이언트 종료.")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(messages):
            selected_message = messages[int(choice) - 1]
            sock.sendto(selected_message.encode(), (server_ip, server_port))
            print(f"메시지 '{selected_message}' 가 {server_ip}:{server_port} 로 전송되었습니다.")
        else:
            print("잘못된 선택입니다. 다시 시도하세요.")

if __name__ == "__main__":
    request_ip_and_send_messages()
