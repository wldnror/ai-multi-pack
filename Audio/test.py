import pulsectl

pulse = pulsectl.Pulse('loopback-setup')

# 모든 소스와 싱크를 나열
def list_sources_and_sinks():
    print("Sources:")
    for source in pulse.source_list():
        print(f"{source.index}: {source.description}")
    print("Sinks:")
    for sink in pulse.sink_list():
        print(f"{sink.index}: {sink.description}")

# 특정 소스를 특정 싱크로 연결
def connect_source_to_sink(source_name, sink_description):
    sources = pulse.source_list()
    sinks = pulse.sink_list()
    source = next((s for s in sources if source_name in s.description), None)
    sink = next((s for s in sinks if sink_description in s.description), None)
    
    if source and sink:
        module_id = pulse.module_load('module-loopback', f'source={source.name} sink={sink.name}')
        print(f"Connected {source.description} to {sink.description} with module id {module_id}")
    else:
        print("Source or sink not found.")

# 사용 예
list_sources_and_sinks()
connect_source_to_sink('loopback', 'USB Speaker')

