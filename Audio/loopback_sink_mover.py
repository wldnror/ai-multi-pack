import pulsectl

pulse = pulsectl.Pulse('audio-stream-manager')

def move_all_loopback_streams(descriptions):
    # 모든 설명을 소문자로 변환하고 공백을 제거
    normalized_descriptions = [desc.lower().replace(" ", "") for desc in descriptions]
    
    try:
        sinks = pulse.sink_list()
        sink_inputs = pulse.sink_input_list()

        # 사용 가능한 싱크 목록 출력
        print("Available Sinks:")
        for sink in sinks:
            print(f"Sink Index: {sink.index}, Name: {sink.name}, Description: {sink.description}")

        # 원하는 싱크 찾기
        target_sink = None
        for sink in sinks:
            normalized_desc = sink.description.lower().replace(" ", "")
            if any(desc in normalized_desc for desc in normalized_descriptions):
                target_sink = sink
                break

        if not target_sink:
            print("No matching sink found for given descriptions.")
            return

        # 스트림 목록 출력
        print("Available Streams:")
        for stream in sink_inputs:
            print(f"Stream Index: {stream.index}, Name: {stream.name}, Description: {stream.proplist.get('application.name')}")

        # 이름이 'loopback'으로 시작하는 모든 스트림 찾아서 이동
        for stream in sink_inputs:
            if stream.name.startswith('loopback'):
                pulse.sink_input_move(stream.index, target_sink.index)
                print(f"Moved stream {stream.name} to sink {target_sink.description}")

    finally:
        pulse.close()

# 여러 언어로 된 설명을 리스트로 전달
move_all_loopback_streams(['Built-in Audio Analog Stereo', '내장 오디오 아날로그 스테레오'])
