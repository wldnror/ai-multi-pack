import pulsectl
import time

pulse = pulsectl.Pulse('audio-switcher')

def set_default_sink_by_name(name_pattern, fallback_name):
    # 모든 출력 장치를 검색
    sinks = pulse.sink_list()
    for sink in sinks:
        if name_pattern in sink.name:
            # 일치하는 패턴이 있을 때 기본 장치로 설정
            pulse.default_set(sink)
            print(f"Default audio device set to: {sink.name}")
            return
    # 일치하는 패턴이 없을 때 fallback 설정
    for sink in sinks:
        if fallback_name in sink.description:
            pulse.default_set(sink)
            print(f"Default audio device set to fallback: {sink.name}")

def monitor_usb_devices():
    while True:
        # 연결된 USB 오디오 장치 찾기
        sinks = pulse.sink_list()
        usb_sinks = [sink for sink in sinks if 'usb' in sink.description.lower()]
        if usb_sinks:
            # USB 오디오 장치가 있다면 기본 장치로 설정
            pulse.default_set(usb_sinks[0])
            print(f"USB audio device detected and set to default: {usb_sinks[0].name}")
        # 10초마다 체크
        time.sleep(10)

# USB 오디오 장치 모니터링 시작
monitor_usb_devices()

# 'loopback-936_12' 패턴을 갖는 장치를 'Built-in Audio Analog Stereo'로 설정
set_default_sink_by_name('loopback-936_12', 'Built-in Audio Analog Stereo')
