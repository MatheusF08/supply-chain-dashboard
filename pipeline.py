# pipeline.py

import os
import pandas as pd
from dotenv import load_dotenv

# Importa as classes da nossa nova arquitetura
from providers.marinetraffic_provider import MarineTrafficProvider
# from providers.kpler_provider import KplerProvider # (Deixamos comentado para o futuro)
from services.vessel_service import VesselService

def main():
    """
    Pipeline principal para coleta de dados de navios usando a arquitetura de provedores.
    """
    print("🚀 Iniciando Pipeline de Dados Híbrido...")
    load_dotenv()

    # --- Seleção do Provedor (Aqui está a mágica da arquitetura) ---
    # Para o MVP, usamos MarineTraffic diretamente.
    marinetraffic_api_key = os.getenv("MARINETRAFFIC_API_KEY")
    
    if not marinetraffic_api_key or "SUA_CHAVE" in marinetraffic_api_key:
        print("\n❌ ERRO: Chave de API 'MARINETRAFFIC_API_KEY' não encontrada ou não configurada no arquivo .env.")
        print("Por favor, obtenha uma chave da MarineTraffic e adicione-a ao arquivo .env.")
        return

    # Instancia o provedor que queremos usar
    try:
        provider = MarineTrafficProvider(api_key=marinetraffic_api_key)
    except ValueError as e:
        print(f"❌ ERRO ao instanciar o provedor: {e}")
        return
    
    # (No futuro, você poderia ter uma lógica para escolher o provedor)
    # if plano == "premium":
    #     provider = KplerProvider(...)
    # else:
    #     provider = MarineTrafficProvider(...)
    # ----------------------------------------------------------------

    # Instancia o serviço com o provedor escolhido
    vessel_service = VesselService(provider=provider)

    # Lista de IMOs para a PoC (substitua pelos do Nelson)
    imo_list_poc = [9811000, 9839172, 9863297, 9462757, 9780882]
    print(f"\nMonitorando {len(imo_list_poc)} navios: {imo_list_poc}")

    # Executa o serviço para obter os dados
    df = vessel_service.get_fleet_data(imo_list_poc)

    if df.empty:
        print("\nPipeline concluído, mas nenhum dado foi salvo.")
        return

    # Converte para DataFrame e salva
    print(f"\n✅ Sucesso! {len(df)} registros de posição foram coletados.")
    
    output_filename = "poc_dados_frota.csv"
    df.to_csv(output_filename, index=False)
    print(f"\n💾 Dados salvos com sucesso em: {output_filename}")
    print("\nPipeline concluído.")


if __name__ == "__main__":
    main()

