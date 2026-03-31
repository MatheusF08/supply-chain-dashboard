# Nome do arquivo: main.py (Nosso Gerador de Dados Falsos)
import os
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import smtplib
from email.mime.text import MIMEText

def buscar_dados_navio_MOCK(imo_number):
    """Simula uma chamada de API e retorna um dicionário rico de dados de exemplo."""
    time.sleep(0.5)
    portos_destino = ["Porto de Santos", "Porto de Paranaguá", "Porto de Itajaí", "Porto de Roterdã"]
    cargas_possiveis = ["Contêineres", "Soja a Granel", "Minério de Ferro", "Petróleo Cru", "Veículos"]
    status_possiveis = ["Em Rota", "Ancorado", "Atracado"]
    agora = datetime.now()
    
    if imo_number == 9839172:
        horas_para_chegar = random.uniform(1, 47)
        eta_falso = agora + timedelta(hours=horas_para_chegar)
        status_atual = "Em Rota"
        disponibilidade = "Contratado"
    else:
        dias_para_chegar = random.randint(3, 20)
        eta_falso = agora + timedelta(days=dias_para_chegar)
        status_atual = random.choice(status_possiveis)
        disponibilidade = random.choice(["Contratado", "Disponível para Frete"])

    partida_falsa = eta_falso + timedelta(days=random.randint(2, 5))

    dados_navio = {
        "ETA Previsto": eta_falso, # Deixa como objeto datetime
        "Porto de Destino": random.choice(portos_destino),
        "Status do Navio": status_atual,
        "Carga Atual": random.choice(cargas_possiveis) if disponibilidade == "Contratado" else "N/A (Vazio)",
        "Disponibilidade": disponibilidade,
        "Próxima Partida Estimada": partida_falsa, # Deixa como objeto datetime
    }
    return dados_navio

def main():
    print("🚀 Iniciando Gerador de Dados Falsos (MODO MOCK)...")
    
    # Usaremos uma lista fixa aqui para não depender do navios.csv
    lista_imos_mock = [9811000, 9839172, 9863297, 9462757, 9780882]
    nomes_navios = ["Ever Given", "CMA CGM Jacques Saade", "HMM Algeciras", "MSC Gulsun", "OOCL Hong Kong"]

    lista_resultados = []
    for i, imo in enumerate(lista_imos_mock):
        print(f"  > Gerando dados para {nomes_navios[i]} (IMO: {imo})")
        dados_completos = buscar_dados_navio_MOCK(imo)
        dados_completos['Nome do Navio'] = nomes_navios[i]
        dados_completos['IMO'] = imo
        dados_completos['Consulta em'] = datetime.now()
        lista_resultados.append(dados_completos)

    resultados_df = pd.DataFrame(lista_resultados)
    colunas_ordenadas = [
        'Nome do Navio', 'IMO', 'Status do Navio', 'ETA Previsto', 'Porto de Destino', 
        'Próxima Partida Estimada', 'Carga Atual', 'Disponibilidade', 'Consulta em'
    ]
    resultados_df = resultados_df[colunas_ordenadas]
    
    # NOME DO ARQUIVO DE SAÍDA DO MOCK
    output_filename = "mock_dados_frota.csv"
    resultados_df.to_csv(output_filename, index=False)
    
    print(f"\n✅ Dados falsos (ricos) salvos em '{output_filename}'.")

if __name__ == "__main__":
    main()
