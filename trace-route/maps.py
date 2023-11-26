import folium
import requests
import socket
from collections import OrderedDict
import subprocess

class Maps:

    def __init__(self):
        self.servidores = OrderedDict()
        self.adicionar_local()
    
    def adicionar_local(self):
        ip_local = requests.get("http://ipv4.icanhazip.com").text.strip()
        self.cidade(ip_local)
        
            
    def cidade(self, ip):
        try:
            info = requests.get(f"http://ip-api.com/json/{ip}")
            info_json = info.json()

            if 'lat' in info_json and 'lon' in info_json:
                coordenadas = (info_json['lat'], info_json['lon'])
                self.servidores[ip] = coordenadas

            if 'city' in info_json:
                return info_json['city']
            else:
                return "Cidade não disponível"

        except requests.exceptions.RequestException as e:
            return "Erro na solicitação"

    def criar_mapa(self):
        if not self.servidores:
            print("Nenhum servidor encontrado para criar o mapa.")
            return

        mapa = folium.Map(location=list(self.servidores.values())[0], zoom_start=2)

        for ip, coordenadas in self.servidores.items():
            folium.Marker(location=coordenadas, popup=f"IP: {ip}").add_to(mapa)

        coordenadas = list(self.servidores.values())
        folium.PolyLine(locations=coordenadas, color="blue", weight=2.5, opacity=1).add_to(mapa)

        mapa.save("mapa_servidores.html")
        print("Mapa salvo como 'mapa_servidores.html'")

