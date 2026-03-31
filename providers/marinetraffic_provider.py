# providers/marinetraffic_provider.py

import requests
import time
from .base_provider import VesselDataProvider

class MarineTrafficProvider(VesselDataProvider):
    """
    Implementação do provedor de dados usando a API legada da MarineTraffic.
    """
    def __init__(self, api_key: str):
        if not api_key or "SUA_CHAVE" in api_key:
            raise ValueError("A chave da API da MarineTraffic é necessária e não foi configurada corretamente.")
        self.api_key = api_key
        # A chave da API vai diretamente na URL para este serviço
        self.base_url = f"https://services.marinetraffic.com/api/exportvessel/{self.api_key}/v:6"

    def get_vessel_data(self, imo_list: list ) -> list:
        all_vessel_data = []
        print(f"🚢 Usando o provedor: MarineTraffic")
        
        for idx, imo in enumerate(imo_list, start=1):
            print(f"  [{idx}/{len(imo_list)}] Buscando dados para o IMO: {imo}")
            # Monta a URL completa para a requisição
            url = f"{self.base_url}/timespan:1440/imo:{imo}/protocol:jsono"
            
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and data:
                        # A API retorna uma lista de posições, pegamos a mais recente (a primeira)
                        latest_record = data[0]
                        latest_record['IMO'] = imo # Garante que o IMO está presente
                        latest_record['SOURCE'] = 'MarineTraffic' # Adiciona a origem do dado
                        all_vessel_data.append(latest_record)
                        print(f"  ✅  Sucesso! Dados recebidos para o IMO {imo}.")
                    else:
                        print(f"  ⚠️  Sucesso, mas nenhum dado retornado para o IMO {imo}.")
                else:
                    # Tenta decodificar a mensagem de erro se não for 200
                    error_message = response.text
                    try:
                        error_json = response.json()
                        if 'description' in error_json:
                            error_message = error_json['description']
                    except:
                        pass # Mantém a mensagem de texto se não for JSON
                    print(f"  ❌  Falha na requisição para o IMO {imo}: {response.status_code} - {error_message}")

            except Exception as e:
                print(f"  ❌  Ocorreu uma exceção para o IMO {imo}: {e}")
            
            if idx < len(imo_list):
                time.sleep(1) # Pausa de 1 segundo para não sobrecarregar a API

        return all_vessel_data
