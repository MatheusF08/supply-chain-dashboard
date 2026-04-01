# services/vessel_service.py

import pandas as pd
from providers.base_provider import BaseVesselProvider

class VesselService:
    """
    Orquestra a obtenção de dados de navios, usando um provedor específico.
    """
    def __init__(self, provider: BaseVesselProvider):
        self.provider = provider
        print("✅ Serviço de Navios pronto para operar.")

    def get_fleet_data(self, imo_list: list) -> pd.DataFrame:
        """
        Busca dados para uma frota específica.
        """
        return self.provider.get_vessel_data(imo_list)

    def find_vessels_by_port(self, port_name: str) -> pd.DataFrame:
        """
        Busca navios em um porto específico.
        """
        return self.provider.find_vessels_by_port(port_name)
