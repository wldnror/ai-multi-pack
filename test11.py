import pulsectl

pulse = pulsectl.Pulse('audio-stream-manager')

def move_stream_to_sink(stream_name, sink_description):
    try:
        # 모든 싱크와 스트림 리스트 가져오기
        sinks = pulse.sink_list()
        sink_inputs = pulse.sink_input_list()
        
        # 원하는 싱크 찾기
        target_sink = next((sink for sink in sinks if sink_description in sink.description), None)
        if not target_sink:
            print(f"Sink with description '{sink_description}' not found.")
            return

        # 스트림 찾아서 이동
        for stream in sink_inputs:
            if stream_name in stream.name:
                pulse.sink_input_move(stream.index, target_sink.index)
                print(f"Moved stream {stream.name} to sink {target_sink.description}")
                return

        print(f"Stream with name '{stream_name}' not found.")

    finally:
        pulse.close()

move_stream_to_sink('loopback-948-12', 'Built-in Audio Analog Stereo')
