import os
import time
import shutil
from threading import Thread
from queue import Queue
from mpu6050 import mpu6050  # MPU-6050 센서 라이브러리

# 충격 감지 기준값 설정
threshold = 10  # 필요에 따라 조정

def shock_event_handler():
    sensor = mpu6050(0x68)  # MPU-6050 센서 객체 생성

    while True:
        # 충격 감지 이벤트 처리
        acceleration_data = sensor.get_accel_data()
        # 충격 감지 기준에 따라 처리
        if acceleration_data['x'] > threshold or acceleration_data['y'] > threshold or acceleration_data['z'] > threshold:
            # 충격 감지 시 현재 녹화 중인 파일 복사
            current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
            current_recording = os.path.join(os.path.dirname(__file__), 'video', f'video_{current_time}.mp4')
            new_recording = os.path.join(os.path.dirname(__file__), 'shock_videos', f'shock_video_{current_time}.mp4')
            shutil.copy(current_recording, new_recording)
            print(f"충격을 감지하여 녹화 파일을 복사했습니다: {new_recording}")
            # 필요한 경우 FTP 업로드 등 다른 작업 수행 가능

# 충격 감지 스레드 시작
shock_thread = Thread(target=shock_event_handler)
shock_thread.start()

# 기존 코드 유지
