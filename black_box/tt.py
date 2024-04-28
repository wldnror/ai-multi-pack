import smbus
import time
import shutil
import os

# MPU-6050 설정
bus = smbus.SMBus(1)  # Raspberry Pi의 I2C 인터페이스 사용
address = 0x68       # MPU-6050의 I2C 주소

# 파일 상태 관리를 위한 전역 변수
current_recording_file = None
recording_in_progress = False

def read_acceleration(addr):
    # 레지스터에서 가속도 데이터 읽기
    raw_data = bus.read_i2c_block_data(addr, 0x3B, 6)
    x = (raw_data[0] << 8) + raw_data[1]
    y = (raw_data[2] << 8) + raw_data[3]
    z = (raw_data[4] << 8) + raw_data[5]
    return x, y, z

def init_sensor():
    # MPU-6050 초기화
    bus.write_byte_data(address, 0x6B, 0)  # 장치 활성화

def copy_last_two_videos(output_directory, impact_time):
    # 가장 최근 두 개의 원본 비디오 파일만 찾아 복사
    video_files = sorted(
        [f for f in os.listdir(output_directory) if not f.startswith('충격녹화')],
        key=lambda x: os.path.getmtime(os.path.join(output_directory, x)),
        reverse=True
    )
    global recording_in_progress
    while recording_in_progress:
        print("녹화 중인 파일 완료 대기중...")
        time.sleep(1)

    if len(video_files) >= 1:
        for file in video_files[:2]:  # 최근 두 개 파일만 복사
            src = os.path.join(output_directory, file)
            dst = os.path.join(output_directory, f"충격녹화_{impact_time}_{file}")
            shutil.copy(src, dst)
            print(f"파일 {file}이 {dst}로 복사되었습니다.")

def monitor_impact(threshold, output_directory):
    init_sensor()
    try:
        while True:
            x, y, z = read_acceleration(address)
            print(f"Acceleration X: {x}, Y: {y}, Z: {z}")  # 센서 데이터 출력
            if abs(x) + abs(y) + abs(z) > threshold:
                current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                print(f"충격 감지: {current_time}")
                copy_last_two_videos(output_directory, current_time)
            time.sleep(1)
    except KeyboardInterrupt:
        print("모니터링 중단")

def start_ffmpeg_recording(output_filename):
    global recording_in_progress, current_recording_file
    recording_in_progress = True
    current_recording_file = output_filename
    # FFmpeg 녹화 시작 명령어 (실제 코드에서는 subprocess 등을 사용할 것)
    print(f"녹화 시작: {output_filename}")
    # 이 부분에 FFmpeg 녹화 명령을 넣으세요
    time.sleep(10)  # 예시로 10초 녹화
    recording_in_progress = False
    print(f"녹화 완료: {output_filename}")

if __name__ == "__main__":
    video_directory = '/home/user/LED/black_box/video'  # 실제 비디오 파일 디렉터리 경로로 수정
    impact_threshold = 10000  # 충격 감지 임계값 설정
    monitor_impact(impact_threshold, video_directory)

