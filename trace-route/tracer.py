import argparse
import socket
import tabulate
import maps
import packets
import tracer_reverso

MAX_TTL = 32
PORT = 33434
PORT_TCP = 80
TIMEOUT = 2

def main():
    parser = argparse.ArgumentParser(description='Documentação trace')
    parser.add_argument('destino')
    parser.add_argument('--ttl', type=int, default=MAX_TTL, help=f'Definir um número de TTL diferente do padrão ({MAX_TTL})')
    parser.add_argument('--mapa', action='store_true', help='Gerar mapa exibindo a rota realizada')
    parser.add_argument('--ouvinte', action='store_true', help='Deixar o trace ouvindo para receber requisições de um trace reverso')
    parser.add_argument('--reverso', action='store_true', help='Realizar um trace reverso')
    parser.add_argument('--protocolo', choices=['tcp', 'udp', 'icmp'], default='udp', help='Especificar o protocolo (tcp, udp, icmp)')
    args = parser.parse_args()

    if args.ouvinte:
        tracer_reverso.ouvindo()

    elif args.reverso:
        enviar_ping(args.destino, args.protocolo)
        esperar_trace_reverso()
        trace_route(args.destino, args.ttl, args.mapa, args.protocolo)

    else:
        trace_route(args.destino, args.ttl, args.mapa, args.protocolo)

def trace_route(destino, time_to_live=MAX_TTL, mapa=False, protocolo='udp'):
    if protocolo not in ['tcp', 'udp', 'icmp']:
        print("Protocolo não suportado.")
        return

    localizacao = maps.maps()

    for TTL in range(1, time_to_live + 1):
        if protocolo == 'udp':
            trace_udp(destino, TTL, mapa, localizacao)
        elif protocolo == 'tcp':
            trace_tcp(destino, TTL, mapa, localizacao)
        elif protocolo == 'icmp':
            trace_icmp(destino, TTL, mapa, localizacao)

def trace_udp(destino, TTL, mapa, localizacao):
    socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    socRecebe.bind(('', PORT))
    socRecebe.settimeout(TIMEOUT)

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
        trace_tcp(destino, TTL, mapa, localizacao)

def trace_tcp(destino, TTL, mapa, localizacao):
    socEnvioTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socEnvioTCP.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

    try:
        socEnvioTCP.connect((destino, PORT_TCP))
        socEnvioTCP.send(b"GET / HTTP/1.1\r\n\r\n")
        socEnvioTCP.recv(1024)  # Ajuste conforme necessário
        socEnvioTCP.close()

        print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [destino, TTL, 'TCP', localizacao.cidade(destino)]], tablefmt='heavy_grid'))

    except socket.error:
        print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], ['DESCONHECIDO', TTL, 'TCP', 'Silent Hill']], tablefmt='heavy_grid'))

def trace_icmp(destino, TTL, mapa, localizacao):
    socEnvioICMP = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    socEnvioICMP.bind(('0.0.0.0', 0))
    socEnvioICMP.settimeout(TIMEOUT)
    
    pacote_icmp = packets.criar_pacote_icmp(TTL)
    socEnvioICMP.sendto(pacote_icmp, (destino, 0))

    try:
        buffer, addr = socEnvioICMP.recvfrom(1024)
        print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'ICMP', localizacao.cidade(addr[0])]], tablefmt='heavy_grid')) 

        if addr[0] == ip:
            break
    except socket.timeout:
        print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], ['DESCONHECIDO', TTL, 'ICMP', 'Silent Hill']], tablefmt='heavy_grid'))

        if addr[0] == ip:
            break

def enviar_ping(destino, protocolo, i=0):
    if protocolo == 'udp':
        socPing = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        udp_packet = packets.criar_pacote_udp()

        while i < 5:
            socPing.sendto(udp_packet, (destino, PORT))
            i += 1

    elif protocolo == 'tcp':
        socPing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            socPing.connect((destino, PORT_TCP))
            socPing.send(b"GET / HTTP/1.1\r\n\r\n")
            socPing.recv(1024)  # Ajuste conforme necessário
            socPing.close()

        except socket.error:
            pass

    elif protocolo == 'icmp':
        socPing = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        pacote_icmp = packets.criar_pacote_icmp(1)

        while i < 5:
            socPing.sendto(pacote_icmp, (destino, 0))
            i += 1

def esperar_trace_reverso():
    pass

if __name__ == '__main__':
    main()

