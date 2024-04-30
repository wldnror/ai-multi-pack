# 예시: serve1.py
def run(conn):
    while True:
        message = conn.recv()
        print(f"serve1 received: {message}")
        # 메시지에 따라 작업 수행
        if message == "button1":
            print("serve1 handling button1")
