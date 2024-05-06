import subprocess
import time

def run_scripts():
    try:
        # snd-aloop 모듈 로드
        subprocess.run(['sudo', 'modprobe', 'snd-aloop'], check=True)
        print("snd-aloop 모듈 로드 완료")
        time.sleep(1)  # 첫 번째 동작 후 2초 대기
    except subprocess.CalledProcessError as e:
        print(f"Error loading snd-aloop module: {e}")
        time.sleep(1)  # 오류 발생 후 2초 대기

    try:
        # 첫 번째 스크립트 실행
        subprocess.run(['/usr/bin/python3', '/home/user/ai-multi-pack/Audio/loopback_sink_mover.py'], check=True)
        print("첫 번째 스크립트 실행 완료")
        time.sleep(1)  # 두 번째 동작 후 2초 대기
    except subprocess.CalledProcessError as e:
        print(f"Error in first script: {e}")
        time.sleep(1)  # 오류 발생 후 2초 대기

    try:
        # 두 번째 스크립트 실행
        subprocess.run(['/usr/bin/python3', '/home/user/ai-multi-pack/Audio/set_default_usb_audio.py'], check=True)
        print("두 번째 스크립트 실행 완료")
    except subprocess.CalledProcessError as e:
        print(f"Error in second script: {e}")

if __name__ == "__main__":
    run_scripts()
