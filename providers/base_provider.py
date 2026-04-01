# providers/base_provider.py

from abc import ABC, abstractmethod
import pandas as pd

class BaseVesselProvider(ABC):
    """
    Classe base abstrata para qualquer provedor de dados de navios.
    Define os métodos que todas as implementações concretas devem ter.
    """
    
    @abstractmethod
    def get_vessel_data(self, imo_list: list) -> pd.DataFrame:
        """
        Busca os dados mais recentes para uma lista de navios (IMOs).
        
        Args:
            imo_list: Uma lista de números IMO.
            
        Returns:
            Um DataFrame do Pandas com os dados dos navios.
            Retorna um DataFrame vazio se nenhum dado for encontrado.
        """
        pass

    @abstractmethod
    def find_vessels_by_port(self, port_name: str) -> pd.DataFrame:
        """
        Busca navios em um porto específico.
        
        Args:
            port_name: O nome do porto a ser buscado.
            
        Returns:
            Um DataFrame do Pandas com os navios encontrados.
            Retorna um DataFrame vazio se nenhum dado for encontrado.
        """
        pass
