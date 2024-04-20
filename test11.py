import pulsectl

pulse = pulsectl.Pulse('audio-device-listener')

try:
    sinks = pulse.sink_list()
    for sink in sinks:
        print(f"Sink Name: {sink.name}, Description: {sink.description}")
finally:
    pulse.close()
