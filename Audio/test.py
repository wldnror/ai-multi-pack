import pulsectl

pulse = pulsectl.Pulse('audio-manager')

def set_default_usb_speaker():
    sinks = pulse.sink_list()
    # 싱크의 이름에서 'usb'를 포함하는 것을 찾습니다.
    usb_speakers = [sink for sink in sinks if 'usb' in sink.name]
    if usb_speakers:
        pulse.default_set(usb_speakers[0])
        print(f"Default audio device set to USB speaker: {usb_speakers[0].description}")
    else:
        print("No USB speakers found.")

set_default_usb_speaker()
