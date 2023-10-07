import binascii
import socket
import sys
import platform
import subprocess
import re
import ipaddress

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

def calculate_network(ip_address, netmask):
    try:
        # Create an IPv4 network with the provided IP address and netmask
        network = ipaddress.IPv4Network(f'{ip_address}/{netmask}', strict=False)

        # Get the network address and broadcast address
        network_address = network.network_address
        broadcast_address = network.broadcast_address

        return network_address, broadcast_address

    except ValueError as e:
        return str(e)
    

try:
    if len(sys.argv) == 4:
        ip = sys.argv[1]
        netmask = sys.argv[2]
        mac = sys.argv[3]
        
        macOK = re.fullmatch(r'^([A-F0-9]{2}(([:][A-F0-9]{2}){5}|([-][A-F0-9]{2}){5})|([\s][A-F0-9]{2}){5})|([a-f0-9]{2}(([:][a-f0-9]{2}){5}|([-][a-f0-9]{2}){5}|([\s][a-f0-9]{2}){5}))$', mac)
        ipOK = re.fullmatch(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$',ip)
        netmaskOK = re.fullmatch(r'^(0|[1-9]|[12]\d|3[0-2])$',netmask)

        if macOK and ipOK and netmaskOK:
            network, broadcast = calculate_network(ip, netmask)
            print(f"-------------------------------------")
            print(f"Network address: {network}")
            print(f"IP address: {ip}")
            print(f"Broadcast address: {broadcast}")
            print(f"MAC address: {mac}")
            print(f"-------------------------------------")

            rtt = -1
            cnt = 0
            while rtt == -1:
                send_wol_packet(str(broadcast), mac)

                rtt = ping_ip(ip, 2)
                cnt+=1

                if rtt == -1:
                    print(f"Ping {ip}: ({cnt}) Timeout", end='\r')
                else:
                    print(f"Ping {ip}: {rtt} ms       ")
        else:
            print(f"")
            print(f"MAC format: AA:BB:CC:DD:EE:FF")
            print(f"IP format: A.B.C.D")
            print(f"Netmask format: A")
            print(f"")
            raise ValueError('Incorrect parameters')



    else:
        print(f"Usage")
        print(f"wol.py IP Netmask MAC")
        print(f"wol.py A.B.C.D E FF:GG:HH:II:JJ:KK")
        
except KeyboardInterrupt:
    print(f"Aborted")
    pass
