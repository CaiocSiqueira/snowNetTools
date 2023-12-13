import socket

def scan_alvo(alvo, portas):
    for porta in range(1,portas):
        scan_individual(alvo, porta)

def scan_individual(ip, porta):
    try:
        soc = socket.socket()
        soc.connect((ip, porta))
        soc.settimeout(1)
        print('Porta aberta: ' + str(porta))
        soc.close()
    except socket.error:
        pass
        # print('Porta fechada: ' + str(porta))

alvo = input("Digite o ip alvo ")
portas = int(input("Digite ate qual porta o scaner deve agir "))

scan_alvo(alvo, portas)
