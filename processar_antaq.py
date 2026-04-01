# processar_antaq.py (VERSÃO OTIMIZADA - APENAS SANTOS)

import pandas as pd
import requests
import zipfile
import io
import os

def baixar_e_processar_dados_antaq(ano: int, porto_filtro: str):
    print(f"Iniciando o processo para o ano de {ano}, filtrando apenas para o porto: {porto_filtro}...")
    # ... (o resto do código de download e limpeza inicial é o mesmo)
    # ... (cole o código completo que está abaixo)
# processar_antaq.py (VERSÃO OTIMIZADA - APENAS SANTOS)

import pandas as pd
import requests
import zipfile
import io
import os

def baixar_e_processar_dados_antaq(ano: int, porto_filtro: str):
    """
    Baixa, processa e salva os dados da ANTAQ, mas filtrando para um único porto
    para reduzir o consumo de memória no Streamlit Cloud.
    """
    print(f"Iniciando o processo para o ano de {ano}, filtrando apenas para o porto: {porto_filtro}...")
    print("Isso pode levar vários minutos, por favor, aguarde...")

    url = f"https://web3.antaq.gov.br/ea/txt/{ano}.zip"
    nome_arquivo_txt = f"{ano}Atracacao.txt"
    arquivo_saida_csv = "dados_portuarios.csv" # Vamos sobrescrever o arquivo antigo

    try:
        print(f"Baixando dados de: {url}" )
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        print("Download concluído. Descompactando e lendo o arquivo...")
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open(nome_arquivo_txt) as f:
                df = pd.read_csv(f, delimiter=';', encoding='utf-8-sig', decimal=',', low_memory=False)
    except Exception as e:
        print(f"ERRO: Falha ao baixar ou processar o arquivo. Detalhes: {e}")
        return

    print("Dados brutos carregados. Iniciando limpeza e transformação...")
    
    df.columns = df.columns.str.replace('Ã§', 'c').str.replace('Ã£', 'a').str.replace('Ã\xad', 'i')
    
    mapa_de_nomes = {
        'Porto Atracação': 'Porto',
        'Tipo de Navegação da Atracação': 'Navegacao',
        'Data Chegada': 'Chegada',
        'Data Atracação': 'Atracacao',
        'Data Desatracação': 'Desatracacao',
        'Carga Total': 'CargaTotal'
    }
    df.rename(columns=mapa_de_nomes, inplace=True)

    colunas_essenciais = ['Chegada', 'Atracacao', 'Desatracacao', 'Porto']
    colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]
    if colunas_faltando:
        print(f"ERRO CRÍTICO: Colunas essenciais não encontradas: {colunas_faltando}")
        return

    # --- OTIMIZAÇÃO PRINCIPAL: FILTRAR ANTES DE PROCESSAR ---
    # Precisamos garantir que a coluna 'Porto' exista antes de filtrar
    if 'Porto' in df.columns:
        print(f"Filtrando dados apenas para o porto: {porto_filtro}")
        df = df[df['Porto'] == porto_filtro].copy()
    else:
        print("ERRO: A coluna 'Porto' não foi encontrada para aplicar o filtro.")
        return

    for col in ['Chegada', 'Atracacao', 'Desatracacao']:
        df[col] = pd.to_datetime(df[col], format='%d/%m/%Y %H:%M:%S', errors='coerce')

    df.dropna(subset=colunas_essenciais, inplace=True)
    
    print("Calculando tempos de espera e operação...")
    df['TempoEsperaAtracacao'] = (df['Atracacao'] - df['Chegada']).dt.total_seconds() / 3600
    df['TempoAtracado'] = (df['Desatracacao'] - df['Atracacao']).dt.total_seconds() / 3600

    df = df[(df['TempoEsperaAtracacao'] >= 0) & (df['TempoAtracado'] >= 0)]

    colunas_para_salvar = [
        'Porto', 'Complexo Portuário', 'Navegacao', 'Chegada', 'Atracacao', 'Desatracacao',
        'TempoEsperaAtracacao', 'TempoAtracado', 'CargaTotal'
    ]
    colunas_existentes = [col for col in colunas_para_salvar if col in df.columns]
    df_final = df[colunas_existentes]

    df_final.to_csv(arquivo_saida_csv, index=False)
    
    print("-" * 50)
    print(f"SUCESSO! Arquivo OTIMIZADO '{arquivo_saida_csv}' salvo com {len(df_final)} registros (apenas para {porto_filtro}).")
    print("Este arquivo é muito menor e deve funcionar no Streamlit Cloud.")
    print("-" * 50)

if __name__ == "__main__":
    ano_para_processar = 2023 
    porto_para_filtrar = "Santos" # Vamos focar em Santos para a POC
    baixar_e_processar_dados_antaq(ano_para_processar, porto_para_filtrar)
