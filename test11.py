import pulsectl
import time

pulse = pulsectl.Pulse('audio-switcher')

def set_default_sink_by_name(name_pattern, fallback_name):
    while True:
        sinks = pulse.sink_list()
        found = False
        for sink in sinks:
            if name_pattern in sink.name:
                pulse.default_set(sink)
                print(f"Default audio device set to: {sink.name}")
                found = True
                break
        if not found:
            for sink in sinks:
                if fallback_name in sink.description:
                    pulse.default_set(sink)
                    print(f"Default audio device set to fallback: {sink.name}")
        time.sleep(10)  # 10초 마다 체크

def monitor_usb_devices():
    while True:
        sinks = pulse.sink_list()
        usb_sinks = [sink for sink in sinks if 'usb' in sink.description.lower()]
        if usb_sinks:
            pulse.default_set(usb_sinks[0])
            print(f"USB audio device detected and set to default: {usb_sinks[0].name}")
        time.sleep(10)

# 병렬로 두 함수 실행
import threading
threading.Thread(target=monitor_usb_devices).start()
threading.Thread(target=set_default_sink_by_name, args=('loopback-936_12', 'Built-in Audio Analog Stereo')).start()
