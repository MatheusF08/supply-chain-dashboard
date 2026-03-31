# services/vessel_service.py

from providers.base_provider import VesselDataProvider
import pandas as pd

class VesselService:
    """
    Serviço responsável por orquestrar a busca de dados de navios.
    Ele usa um 'provider' para buscar os dados, abstraindo a fonte.
    """
    def __init__(self, provider: VesselDataProvider):
        self.provider = provider

    def get_fleet_data(self, imo_list: list) -> pd.DataFrame:
        """
        Busca os dados da frota e já retorna como um DataFrame do Pandas.
        """
        print(f"🛠️  Serviço de Navios iniciado...")
        
        raw_data = self.provider.get_vessel_data(imo_list)
        
        if not raw_data:
            return pd.DataFrame() # Retorna um DataFrame vazio se não houver dados
            
        return pd.DataFrame(raw_data)

