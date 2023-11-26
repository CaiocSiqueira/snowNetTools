import argparse
import socket
import struct
import tabulate
import requests
from maps import criar_mapa

MAX_TTL = 32
PORT = 33434
PORT_TCP = 80
TIMEOUT = 2

def main():
    parser = argparse.ArgumentParser(description='Documentação trace')
    parser.add_argument('destino')
    parser.add_argument('--ttl', type=int, default=MAX_TTL, help=f'Definir um número de TTL diferente do padrão ({MAX_TTL})')
    parser.add_argument('--maps', action='store_true', help='Gerar mapa exibindo a rota realizada')
    args = parser.parse_args()

    trace_route(args.destino, args.ttl, args.maps)

def trace_route(destino, time_to_live=MAX_TTL, maps=False):
    nos = [0]

    dados_localizacao = {
        "Cidade1": (-23.550520, -46.633307),
        "Cidade2": (40.712776, -74.005974),
        "Cidade3": (51.509865, -0.118092),
    }

    criar_mapa(dados_localizacao)
    
    socEnvio = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    socRecebe = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    socRecebe.bind(('', PORT))
    socRecebe.settimeout(TIMEOUT)

    for TTL in range(1, time_to_live + 1):
        socEnvio.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL)

        udp_header = struct.pack('!HHHH', PORT, PORT, 8, 0)
        udp_packet = udp_header + b'0'
        socEnvio.sendto(udp_packet, (destino, PORT))

        ip = socket.gethostbyname(destino)

        try:
            buffer, addr = socRecebe.recvfrom(1024)
            if addr[0] == ip:
                break
            
            print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'UDP', cidade(addr[0])]], tablefmt='heavy_grid'))
            nos.append(addr[0])

        except socket.timeout:

            socEnvioICMP = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            socEnvioICMP.bind(('0.0.0.0', 0))
            socEnvioICMP.settimeout(TIMEOUT)
            
            pacote_icmp = criar_pacote_icmp(TTL)
            socEnvioICMP.sendto(pacote_icmp, (destino, 0))

            try:
                buffer, addr = socRecebe.recvfrom(1024)
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], [addr[0], TTL, 'ICMP', cidade(addr[0])]], tablefmt='heavy_grid'))
                nos.append(addr[0]) 

                if addr[0] == ip:
                    break
            except socket.timeout:
                print(tabulate.tabulate([['IP', 'TTL', 'PROTOCOLO', 'LOCALIZAÇÃO'], ['DESCONHECIDO', TTL, 'ICMP', 'Silent Hill']], tablefmt='heavy_grid'))
                nos.append('0')

                if addr[0] == ip:
                    break

    qtd = len(nos)
    print(f"{qtd-1} nó(s) até o último nó")

def cidade(ip):
    try:
        info = requests.get(f"https://ipinfo.io/{ip}")

        if info.status_code == 200:
            info_json = info.json()

            if 'city' in info_json:
                return info_json['city']
            else:
                return "Cidade não disponível"
        else:
            return "Falha na solicitação"

    except requests.exceptions.RequestException as e:
        return "Erro na solicitação"
    
def coordenadas(ip):
    try:
        info = requests.get(f"https://ipinfo.io/{ip}")

        if info.status_code == 200:
            info_json = info.json()

            if 'loc' in info_json:
                coordenadas = tuple(map(float, info_json["loc"].split(',')))
                localizacao = {[ip]: coordenadas}

        return localizacao

    except requests.exceptions.RequestException as e:
        return "Erro na solicitação"

    
def criar_pacote_icmp(ttl):
    tipo = 8  # Echo Request
    codigo = 0
    checksum = 0
    identificador = 12345
    sequencia = 0

    header = struct.pack('!BBHHH', tipo, codigo, checksum, identificador, sequencia)
    dados = b'Hello, ICMP!'
    pacote_icmp = header + dados

    checksum = calcula_checksum(pacote_icmp)
    header = struct.pack('!BBHHH', tipo, codigo, checksum, identificador, sequencia)
    pacote_icmp = header + dados

    return pacote_icmp

def calcula_checksum(data):
    length = len(data)
    sum_ = 0
    count_to = (length // 2) * 2
    count = 0

    while count < count_to:
        this_val = data[count + 1] * 256 + data[count]
        sum_ += this_val
        sum_ &= 0xffffffff
        count += 2

    if count_to < length:
        sum_ += data[length - 1]
        sum_ &= 0xffffffff

    sum_ = (sum_ >> 16) + (sum_ & 0xffff)
    sum_ += (sum_ >> 16)
    result = ~sum_ & 0xffff
    result = result >> 8 | ((result & 0xff) << 8)
    return result


if __name__ == '__main__':
    main()

