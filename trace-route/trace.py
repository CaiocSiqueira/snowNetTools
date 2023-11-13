import socket
import struct

MAX_TTL = 64
PORT = 33434

destino = input('Ip de destino: ')

socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

socRecebe.bind(("", PORT))

socRecebe.settimeout(5)

for TTL in range(1, MAX_TTL):
    socEnvio.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)
    
    udp_header = struct.pack('!HHHH', PORT, PORT, 8, 0) 

    udp_packet = udp_header + b'0'

    socEnvio.sendto(udp_packet, (destino, PORT))

    try:
        buffer, addr = socRecebe.recvfrom(1024)
        print(f"Resposta de {addr[0]}")
    except socket.timeout:
        print("* Timeout")
