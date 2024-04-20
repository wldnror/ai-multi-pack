import pulsectl

pulse = pulsectl.Pulse('loopback-source-finder')

def list_all_sources():
    print("Sources:")
    for source in pulse.source_list():
        print(f"{source.index}: {source.name} - {source.description}")

def find_loopback_sources():
    loopback_sources = []
    sources = pulse.source_list()
    for source in sources:
        if source.description.startswith('loopback'):
            loopback_sources.append(source)
            print(f"Found loopback source: {source.index} - {source.description}")
    return loopback_sources

list_all_sources()
loopback_sources = find_loopback_sources()
