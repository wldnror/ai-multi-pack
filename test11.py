import pulsectl

pulse = pulsectl.Pulse('audio-stream-listener')

try:
    sink_inputs = pulse.sink_input_list()
    for stream in sink_inputs:
        print(f"Stream Index: {stream.index}, Name: {stream.name}, Sink: {stream.sink}")
finally:
    pulse.close()
