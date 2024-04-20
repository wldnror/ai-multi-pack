import subprocess

def unload_and_reload_loopback(source, sink):
    # 현재 로드된 모듈 확인
    result = subprocess.run(['pactl', 'list', 'short', 'modules'], capture_output=True, text=True)
    modules = result.stdout.splitlines()
    for module in modules:
        if 'module-loopback' in module and source in module:
            module_id = module.split()[0]
            # 해당 모듈 언로드
            subprocess.run(['pactl', 'unload-module', module_id])
            # 새 설정으로 모듈 리로드
            load_command = f"pactl load-module module-loopback source={source} sink={sink}"
            subprocess.run(load_command.split())
            print(f"Reloaded loopback from {source} to {sink}")

# 예: 특정 소스를 Samsung USB 스피커로 리디렉션
unload_and_reload_loopback('alsa_input.platform-snd_aloop.0.analog-stereo', 'alsa_output.usb-Samsung_Speaker_Samsung_Speaker-00.analog-stereo')
