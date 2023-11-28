import argparse
import socket
import tabulate
import maps
import packets
import struct
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
    args = parser.parse_args()

    if args.ouvinte:
        tracer_reverso.iniciar_reverso()

    elif args.reverso:
        enviar_ping(args.destino)
        #esperar_trace_reverso(args.destino)
        #trace_route(args.destino, args.ttl, args.mapa)

    else:
        trace_route(args.destino, args.ttl, args.mapa)

def trace_route(destino, time_to_live=MAX_TTL, mapa=False):
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
    if mapa:
        localizacao.criar_mapa()

def enviar_ping(destino, i = 0):
    socPing = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)

    mensagem = "Ping"

    udp_header = struct.pack('!HHHH', PORT, PORT, 8 + len(mensagem), 0)
    udp_packet = udp_header + mensagem.encode('utf-8')

    while i < 5:
        socPing.sendto(udp_packet, (destino, PORT))
        i += 1

def esperar_trace_reverso(ip_trace_reverso):
    recebe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recebe.connect((f'{ip_trace_reverso}', 9100))

    ips_reversos = recebe.recv(1024).decode()
    print(f'Dados Recebidos: {ips_reversos}')

    recebe.close()

if __name__ == '__main__':
    main()

