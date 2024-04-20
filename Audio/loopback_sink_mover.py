import pulsectl

pulse = pulsectl.Pulse('audio-bluetooth-handler')

def move_bluetooth_audio():
    try:
        # 모든 싱크 리스트와 스트림 리스트 가져오기
        sinks = pulse.sink_list()
        sink_inputs = pulse.sink_input_list()

        # USB 스피커와 기본 오디오 싱크 식별
        usb_sink = next((sink for sink in sinks if 'usb' in sink.description.lower()), None)
        default_sink = next((sink for sink in sinks if 'analog-stereo' in sink.description.lower()), None)

        # 블루투스로 연결된 스트림 찾기
        bluetooth_streams = [stream for stream in sink_inputs if 'bluetooth' in stream.name.lower()]

        for stream in bluetooth_streams:
            if usb_sink:
                # USB 스피커가 있으면 거기로 이동
                pulse.sink_input_move(stream.index, usb_sink.index)
                print(f"Moved Bluetooth stream {stream.name} to USB speaker {usb_sink.description}")
            elif default_sink:
                # USB 스피커가 없으면 기본 오디오로 이동
                pulse.sink_input_move(stream.index, default_sink.index)
                print(f"Moved Bluetooth stream {stream.name} to default audio {default_sink.description}")

    finally:
        pulse.close()

move_bluetooth_audio()
