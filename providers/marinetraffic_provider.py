# providers/marinetraffic_provider.py

import pandas as pd
import os
from .base_provider import BaseVesselProvider

class MarineTrafficProvider(BaseVesselProvider):
    """
    Implementação concreta para buscar dados da MarineTraffic (ou simular).
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        print("🚢 Provedor MarineTraffic inicializado.")

    def get_vessel_data(self, imo_list: list) -> pd.DataFrame:
        """
        Simula a busca de dados para uma lista de IMOs.
        Para o MVP, lê os dados do arquivo MOCK.
        """
        print(f"🔎 Buscando dados para {len(imo_list)} navios via MarineTraffic (simulação)...")
        
        # Em um cenário real, aqui iria o código para chamar a API da MarineTraffic
        # usando self.api_key e a imo_list.
        
        # Simulação:
        mock_file = "mock_dados_frota.csv"
        if os.path.exists(mock_file):
            df = pd.read_csv(mock_file)
            # Filtra o dataframe para conter apenas os IMOs da lista
            resultados = df[df['IMO'].isin(imo_list)]
            print(f"✅ {len(resultados)} navios encontrados nos dados MOCK.")
            return resultados
        
        print("⚠️ Arquivo MOCK não encontrado. Retornando vazio.")
        return pd.DataFrame()

    def find_vessels_by_port(self, port_name: str) -> pd.DataFrame:
        """
        Simula a busca de navios em um porto específico.
        Para o MVP, filtra os dados do arquivo MOCK.
        """
        print(f"🔎 Buscando navios no porto '{port_name}' via MarineTraffic (simulação)...")
        
        # Em um cenário real, aqui iria o código para chamar a API
        # com um endpoint de busca por porto.
        
        # Simulação:
        mock_file = "mock_dados_frota.csv"
        if os.path.exists(mock_file):
            df = pd.read_csv(mock_file)
            # Filtra o dataframe pelo nome do porto (ignorando maiúsculas/minúsculas)
            resultados = df[df['Porto de Destino'].str.contains(port_name, case=False, na=False)]
            print(f"✅ {len(resultados)} navios encontrados para '{port_name}' nos dados MOCK.")
            return resultados
            
        print("⚠️ Arquivo MOCK não encontrado. Retornando vazio.")
        return pd.DataFrame()
