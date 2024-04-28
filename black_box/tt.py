import smbus
import time
import shutil
import os

# MPU-6050 설정
bus = smbus.SMBus(1)  # Raspberry Pi의 I2C 인터페이스 사용
address = 0x68       # MPU-6050의 I2C 주소

# 파일 상태 관리 및 가속도 이전 값 저장을 위한 전역 변수
current_recording_file = None
recording_in_progress = False
last_x, last_y, last_z = 0, 0, 0
copied_files_list = set()  # 복사된 파일 목록 관리

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

def detect_impact(x, y, z, threshold):
    global last_x, last_y, last_z
    # 가속도 변화 계산
    delta_x = abs(x - last_x)
    delta_y = abs(y - last_y)
    delta_z = abs(z - last_z)
    # 이전 값을 현재 값으로 업데이트
    last_x, last_y, last_z = x, y, z
    # 변화가 임계값을 초과하는 경우 True 반환
    return (delta_x + delta_y + delta_z) > threshold

def is_file_ready(filepath, timeout=10):
    # 파일이 완전히 쓰여졌는지 확인하는 함수
    initial_size = os.path.getsize(filepath)
    time.sleep(1)
    for _ in range(timeout):
        size = os.path.getsize(filepath)
        if size == initial_size:
            return True
        initial_size = size
        time.sleep(1)
    return False

def copy_last_two_videos(input_directory, output_directory, impact_time):
    video_files = [
        f for f in os.listdir(input_directory)
        if f.endswith('.mp4')
    ]
    video_files = sorted(
        video_files,
        key=lambda x: os.path.getmtime(os.path.join(input_directory, x)),
        reverse=True
    )

    # 녹화 중인 파일 완료 대기
    while recording_in_progress:
        print("녹화 중인 파일 완료 대기중...")
        time.sleep(1)

    copied_files = 0
    for file in video_files:
        if copied_files >= 2:
            break
        file_path = os.path.join(input_directory, file)
        file_mod_time = os.path.getmtime(file_path)

        # 파일 이름과 수정 시간을 기반으로 복사된 파일인지 확인
        file_identifier = (file, file_mod_time)
        if is_file_ready(file_path) and file_identifier not in copied_files_list:
            dst = os.path.join(output_directory, f"충격녹화_{impact_time}_{file}")
            shutil.copy(file_path, dst)
            copied_files_list.add(file_identifier)
            print(f"파일 {file}이 {dst}로 복사되었습니다.")
            copied_files += 1


def monitor_impact(threshold, input_directory, output_directory):
    init_sensor()
    try:
        while True:
            x, y, z = read_acceleration(address)
            if detect_impact(x, y, z, threshold):
                current_time = time.strftime("%Y-%m-%d_%H-%M-%S")
                print(f"충격 감지: {current_time}")
                copy_last_two_videos(input_directory, output_directory, current_time)
            time.sleep(1)
    except KeyboardInterrupt:
        print("모니터링 중단")

def start_ffmpeg_recording(output_filename):
    global recording_in_progress, current_recording_file
    recording_in_progress = True
    current_recording_file = output_filename
    print(f"녹화 시작: {output_filename}")
    time.sleep(10)  # 예시로 10초 녹화
    recording_in_progress = False
    current_recording_file = None
    print(f"녹화 완료: {output_filename}")

if __name__ == "__main__":
    input_directory = os.path.join(os.path.dirname(__file__), 'video', '상시녹화')
    output_directory = os.path.join(os.path.dirname(__file__), 'video', '충격녹화')
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    impact_threshold = 80000
    monitor_impact(impact_threshold, input_directory, output_directory)
