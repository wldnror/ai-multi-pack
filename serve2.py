# 예시: serve2.py
def run(conn):
    while True:
        message = conn.recv()
        print(f"serve2 received: {message}")
        # 메시지에 따라 작업 수행
        if message == "button1":
            print("serve2 handling button1")
