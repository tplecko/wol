import binascii
import socket
import sys
import platform
import subprocess

def send_wol_packet(ip_address, mac_address):
    # Create magic packet
    mac_bytes = binascii.unhexlify(mac_address.replace(':', ''))
    magic_packet = b'\xFF' * 6 + mac_bytes * 16

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send magic packet
    sock.sendto(magic_packet, (ip_address, 9))
    sock.close()


def ping_ip(ip_address, timeout=1):
    operating_system = platform.system()

    if operating_system == "Windows":
        ping_command = ["ping", "-n", "1", "-w", str(timeout * 1000), ip_address]
    elif operating_system == "Linux":
        ping_command = ["ping", "-c", "1", "-W", str(timeout), ip_address]
    else:
        raise NotImplementedError(f"Ping not supported on {operating_system}")

    try:
        output = subprocess.check_output(ping_command).decode("utf-8")
        if "time=" in output:
            start = output.find("time=") + 5
            end = output.find("ms", start)
            return float(output[start:end])
        else:
            return -1  # No round trip time found, indicating timeout
    except subprocess.CalledProcessError:
        return -1  # Ping failed, indicating timeout

try:
    if len(sys.argv) == 4:
        ip = sys.argv[1]
        broadcast = sys.argv[2]
        mac = sys.argv[3]

        print(f"-------------------------------------")
        print(f"Target IP address: {ip}")
        print(f"Broadcast address: {broadcast}")
        print(f"Target MAC address: {mac}")
        print(f"-------------------------------------")

        rtt = -1

        while rtt == -1:
            send_wol_packet(broadcast, mac)

            rtt = ping_ip(ip, 2)

            if rtt == -1:
                print(f"Ping {ip}: Timeout {rtt}")
            else:
                print(f"Ping {ip}: {rtt} ms")

    else:
        print(f"wol.py ip broadcast mac")
except KeyboardInterrupt:
    print(f"Aborted")
    pass
