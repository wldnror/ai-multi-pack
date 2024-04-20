import subprocess

def run_scripts():
    # 스크립트 경로 설정
    script1 = 'Audio/set_default_usb_audio.py'
    script2 = 'Audio/loopback_sink_mover.py'

    # 두 스크립트를 동시에 실행하기 위해 subprocess.Popen을 사용
    processes = []
    processes.append(subprocess.Popen(['python', script1]))
    processes.append(subprocess.Popen(['python', script2]))

    # 모든 스크립트가 종료될 때까지 기다림
    for process in processes:
        process.wait()

    print("모든 스크립트 실행 완료")

# 스크립트 실행
run_scripts()
