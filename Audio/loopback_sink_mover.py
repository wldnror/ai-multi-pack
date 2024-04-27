import pulsectl

pulse = pulsectl.Pulse('audio-stream-manager')

def move_all_loopback_streams(sink_description):
    try:
        # 모든 싱크와 스트림 리스트 가져오기
        sinks = pulse.sink_list()
        sink_inputs = pulse.sink_input_list()

        # 스트림 목록 출력
        print("Available Streams:")
        for stream in sink_inputs:
            print(f"Stream Index: {stream.index}, Name: {stream.name}, Description: {stream.proplist.get('application.name')}")

        # 원하는 싱크 찾기
        target_sink = next((sink for sink in sinks if sink_description in sink.description), None)
        if not target_sink:
            print(f"Sink with description '{sink_description}' not found.")
            return

        # 이름이 'loopback'으로 시작하는 모든 스트림 찾아서 이동
        for stream in sink_inputs:
            if stream.name.startswith('loopback'):
                pulse.sink_input_move(stream.index, target_sink.index)
                print(f"Moved stream {stream.name} to sink {target_sink.description}")

    finally:
        pulse.close()

move_all_loopback_streams('Built-in Audio Analog Stereo')
