import pulsectl

pulse = pulsectl.Pulse('audio-listener')

def list_all_sinks():
    sinks = pulse.sink_list()
    for sink in sinks:
        print(f"Sink ID: {sink.index}, Name: {sink.name}, Description: {sink.description}")

list_all_sinks()
