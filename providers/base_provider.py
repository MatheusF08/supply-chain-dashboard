# providers/base_provider.py

from abc import ABC, abstractmethod

class VesselDataProvider(ABC):
    """
    Classe base abstrata para qualquer provedor de dados de navios.
    Define os métodos que todas as implementações concretas devem ter.
    """
    
    @abstractmethod
    def get_vessel_data(self, imo_list: list) -> list:
        """
        Busca os dados mais recentes para uma lista de navios.
        
        Args:
            imo_list: Uma lista de números IMO.
            
        Returns:
            Uma lista de dicionários, onde cada dicionário representa os dados de um navio.
            Retorna uma lista vazia se nenhum dado for encontrado.
        """
        pass

