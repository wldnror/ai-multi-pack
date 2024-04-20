import pulsectl
import time

pulse = pulsectl.Pulse('audio-manager')

def find_sink(description_keyword):
    sinks = pulse.sink_list()
    return next((sink for sink in sinks if description_keyword in sink.description.lower()), None)

def move_stream_to_sink(stream_name_pattern, sink_description):
    streams = pulse.sink_input_list()
    target_sink = find_sink(sink_description)
    if not target_sink:
        print(f"No target sink found for description '{sink_description}'.")
        return

    for stream in streams:
        if stream_name_pattern in stream.name:
            pulse.sink_input_move(stream.index, target_sink.index)
            print(f"Moved stream '{stream.name}' to sink '{target_sink.description}'")

def handle_bluetooth_streams():
    bluetooth_streams = [stream for stream in pulse.sink_input_list() if 'bluetooth' in stream.name.lower()]
    usb_sink = find_sink('usb')
    default_sink = find_sink('analog-stereo')
    target_sink = usb_sink if usb_sink else default_sink

    if not target_sink:
        print("No suitable sink found for Bluetooth streams.")
        return

    for stream in bluetooth_streams:
        pulse.sink_input_move(stream.index, target_sink.index)
        print(f"Moved Bluetooth stream '{stream.name}' to '{target_sink.description}'")

def monitor_and_update():
    while True:
        move_stream_to_sink('loopback', 'Built-in Audio Analog Stereo')
        handle_bluetooth_streams()
        time.sleep(10)  # Check every 10 seconds

monitor_and_update()
