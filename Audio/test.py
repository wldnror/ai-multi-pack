import pulsectl

pulse = pulsectl.Pulse('audio-manager')

def set_default_usb_speaker():
    sinks = pulse.sink_list()
    # 이름에 'usb'가 포함되고, 설명에 오디오 출력과 관련된 키워드가 포함된 싱크를 찾습니다.
    audio_keywords = ['Stereo', 'Speaker', 'Audio', 'Analog']
    usb_speakers = [
        sink for sink in sinks
        if 'usb' in sink.name.lower() and any(keyword in sink.description for keyword in audio_keywords)
    ]
    if usb_speakers:
        pulse.default_set(usb_speakers[0])
        print(f"Default audio device set to USB speaker: {usb_speakers[0].description}")
    else:
        print("No USB speakers found.")

set_default_usb_speaker()
