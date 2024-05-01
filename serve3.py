# 예시: serve3.py
def run(conn):
    while True:
        message = conn.recv()
        print(f"serve3 received: {message}")
        # 메시지에 따라 작업 수행
        if message == "button3":
            print("serve3 handling button1")
