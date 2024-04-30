import socket
import subprocess
import re

def get_ip_address():
    try:
        # 'hostname -I' returns the current IP address(es) of the Raspberry Pi
        result = subprocess.check_output(["hostname", "-I"]).decode("utf-8")
        # Use regex to extract the first valid IP address
        ip_addresses = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', result)
        return ip_addresses[0] if ip_addresses else None
    except subprocess.CalledProcessError:
        return None

# Setup the UDP server
udp_ip = "0.0.0.0"  # Listen on all interfaces
udp_port = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))
print("UDP Server is up and listening...")

while True:
    data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
    print(f"Received message: {data.decode()} from {addr}")

    raspberry_pi_ip = get_ip_address()
    if data and raspberry_pi_ip:
        response = f"My IP address is {raspberry_pi_ip}"
        sock.sendto(response.encode(), addr)

sock.close()
