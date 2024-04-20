import pulsectl

pulse = pulsectl.Pulse('audio-manager')

def set_default_usb_speaker():
    sinks = pulse.sink_list()
    audio_keywords = ['Stereo', 'Speaker', 'Audio', 'Analog']
    usb_speakers = [
        sink for sink in sinks
        if 'usb' in sink.name.lower() and any(keyword in sink.description for keyword in audio_keywords)
    ]
    if usb_speakers:
        pulse.default_set(usb_speakers[0])
        print(f"Default audio device set to USB speaker: {usb_speakers[0].description}")
        # 기본 장치로 모든 스트림 이동
        move_other_streams(usb_speakers[0].index)
    else:
        print("No USB speakers found.")

def move_other_streams(new_default_sink_index):
    sink_inputs = pulse.sink_input_list()
    for stream in sink_inputs:
        # 'loopback'으로 시작하는 스트림을 제외하고 모든 스트림 이동
        if not stream.name.startswith('loopback'):
            pulse.sink_input_move(stream.index, new_default_sink_index)
            print(f"Moved stream {stream.name} to new default sink")

set_default_usb_speaker()
