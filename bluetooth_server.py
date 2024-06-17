import socket
import time
import bluetooth

def get_bluetooth_uuids():
    target_name = "용굴라이더"  # 타겟 블루투스 장치 이름
    target_address = None
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True)

    for addr, name in nearby_devices:
        if target_name == name:
            target_address = addr
            break

    if target_address is not None:
        services = bluetooth.find_service(address=target_address)
        uuids = [service["service-id"] for service in services]
        return uuids
    return []

def broadcast_uuids():
    broadcast_ip = '255.255.255.255'
    broadcast_port = 5005
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        uuids = get_bluetooth_uuids()
        for uuid in uuids:
            message = f"UUID: {uuid}"
            sock.sendto(message.encode(), (broadcast_ip, broadcast_port))
            print(f"Broadcasting: {message}")
            time.sleep(5)  # 5초마다 브로드캐스트

if __name__ == "__main__":
    broadcast_uuids()
