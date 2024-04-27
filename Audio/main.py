import subprocess

def run_scripts():
    # snd-aloop 모듈 로드
    subprocess.run(['sudo', 'modprobe', 'snd-aloop'], check=True)
    print("snd-aloop 모듈 로드 완료")

    # 첫 번째 스크립트 실행
    subprocess.run(['python', 'Audio/loopback_sink_mover.py'], check=True)
    print("첫 번째 스크립트 실행 완료")

    # 두 번째 스크립트 실행
    subprocess.run(['python', 'Audio/set_default_usb_audio.py'], check=True)
    print("두 번째 스크립트 실행 완료")

if __name__ == "__main__":
    run_scripts()
