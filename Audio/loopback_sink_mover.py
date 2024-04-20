import pulsectl

pulse = pulsectl.Pulse('audio-manager')

def set_default_usb_speaker():
    # 모든 싱크(출력 장치)를 검색합니다.
    sinks = pulse.sink_list()
    # USB 스피커를 싱크 목록에서 찾습니다.
    usb_speakers = [sink for sink in sinks if 'usb' in sink.description.lower()]
    if usb_speakers:
        # 첫 번째 USB 스피커를 기본 장치로 설정합니다.
        pulse.default_set(usb_speakers[0])
        print(f"Default audio device set to USB speaker: {usb_speakers[0].description}")
    else:
        print("No USB speakers found.")

def move_loopback_streams():
    # 모든 싱크와 스트림 리스트를 가져옵니다.
    sinks = pulse.sink_list()
    sink_inputs = pulse.sink_input_list()
    # 'Built-in Audio Analog Stereo' 싱크를 찾습니다.
    target_sink = next((sink for sink in sinks if 'Built-in Audio Analog Stereo' in sink.description), None)
    if not target_sink:
        print("Target sink 'Built-in Audio Analog Stereo' not found.")
        return
    # 'loopback'으로 시작하는 모든 스트림을 찾아서 이동합니다.
    for stream in sink_inputs:
        if stream.name.startswith('loopback'):
            pulse.sink_input_move(stream.index, target_sink.index)
            print(f"Moved stream {stream.name} to sink {target_sink.description}")

# USB 스피커를 기본 장치로 설정합니다.
set_default_usb_speaker()
# 'loopback'으로 시작하는 스트림을 특정 싱크로 이동합니다.
move_loopback_streams()
