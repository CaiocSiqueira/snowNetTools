import socket
import struct

MAX_TTL = 64
PORT = 33434

nos = [0]

destino = input('Ip de destino: ')

socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

socRecebe.bind(('', PORT))

socRecebe.settimeout(2)

for TTL in range(1, MAX_TTL):
    socEnvio.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)
    
    udp_header = struct.pack('!HHHH', PORT, PORT, 8, 0) 

    udp_packet = udp_header + b'0'

    socEnvio.sendto(udp_packet, (destino, PORT))

    try:
        buffer, addr = socRecebe.recvfrom(1024)
        if(addr[0] == nos[-1]):
            break

        print(f"Resposta de {addr[0]}")

        nos.append(addr[0])

    except socket.timeout:
        print("* Timeout")
        
        nos.append('0')
    
qtd = len(nos)
    
print(f"{qtd-1} nó(s) até o ultimo nó")