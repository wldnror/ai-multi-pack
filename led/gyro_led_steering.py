import socket
import time
import RPi.GPIO as GPIO

# GPIO 설정
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

def toggle_led(state):
    GPIO.output(LED_PIN, state)

# 소켓 객체 생성
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '127.0.0.1'
port = 12345
server_socket.bind((host, port))
server_socket.listen(1)

print("서버 시작, 클라이언트의 연결을 기다립니다.")
conn, addr = server_socket.accept()
print(f"{addr}에서 연결되었습니다.")

try:
    for i in range(5):
        # LED 상태 토글
        led_state = i % 2 == 0
        toggle_led(led_state)
        # LED 상태를 전송
        conn.send(b'LED ON' if led_state else b'LED OFF')
        time.sleep(1)  # 1초 대기
finally:
    conn.close()
    server_socket.close()
    GPIO.cleanup()
