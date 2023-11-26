import folium
from folium import plugins
import requests

class Maps:

    def __init__(self):
        self.servidores = {}

    def cidade(self, ip):
        try:
            info = requests.get(f"https://ipinfo.io/{ip}")

            if info.status_code == 200:
                info_json = info.json()

                if 'loc' in info_json:
                    coordenadas = tuple(map(float, info_json["loc"].split(',')))
                    self.servidores[ip] = coordenadas
                    
                if 'city' in info_json:
                    return info_json['city']
                else:
                    return "Cidade não disponível"

    
            else:
                return "Falha na solicitação"

        except requests.exceptions.RequestException as e:
            return "Erro na solicitação"
        
    def coordenadas(self, ip):
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

