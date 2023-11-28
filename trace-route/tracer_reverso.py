import socket
import tabulate
import maps
import packets

MAX_TTL = 32
PORT = 33434
PORT_TCP = 80
TIMEOUT = 20

def iniciar_reverso():
    ip_reverso = ouvindo()

    trace_route_reverso(ip_reverso)

def ouvindo():
    print('Aguardando conexoes')

    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    socRecebe.bind(('0.0.0.0', PORT))
    socRecebe.settimeout(TIMEOUT)

    while True:
        try:
            buffer, addr = socRecebe.recvfrom(1024)

            ip_reverso = addr[0]

            print(f"Recebido pacote de {addr}")
            break

        except socket.timeout:
            print("Timeout - Nenhum pacote recebido.")
            break

    socRecebe.close()

    return addr[0]


def trace_route_reverso(destino, time_to_live=MAX_TTL, mapa=False):
    socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    socRecebe.bind(('', PORT))
    socRecebe.settimeout(TIMEOUT)

    localizacao = maps.maps()

    for TTL in range(1, time_to_live + 1):
        socEnvio.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

        udp_packet = packets.criar_pacote_udp()
        
        socEnvio.sendto(udp_packet, (destino, PORT))

        ip = socket.gethostbyname(destino)

        try:
            buffer, addr = socRecebe.recvfrom(1024)
            if addr[0] == ip:
                break
            
            print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'UDP', localizacao.cidade((addr[0]))]], tablefmt='heavy_grid'))
            

        except socket.timeout:

            socEnvioICMP = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            socEnvioICMP.bind(('0.0.0.0', 0))
            socEnvioICMP.settimeout(TIMEOUT)
            
            pacote_icmp = packets.criar_pacote_icmp(TTL)
            socEnvioICMP.sendto(pacote_icmp, (destino, 0))

            try:
                buffer, addr = socRecebe.recvfrom(1024)
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'ICMP', localizacao.cidade(addr[0])]], tablefmt='heavy_grid')) 

                if addr[0] == ip:
                    break
            except socket.timeout:
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], ['DESCONHECIDO', TTL, 'ICMP', 'Silent Hill']], tablefmt='heavy_grid'))

                if addr[0] == ip:
                    break
    
    return localizacao.servidores


