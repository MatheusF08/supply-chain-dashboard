# pipeline_kpler.py - VERSÃO FINAL COM FLUXO OAUTH2 E AUDIENCE

# 1. Import necessary libraries
import requests
import pandas as pd
import os
import time
from dotenv import load_dotenv

# --- CARREGAR VARIÁVEIS DE AMBIENTE ---
load_dotenv()

# Sua chave "Basic" do arquivo .env
BASIC_AUTH_TOKEN = os.getenv("AIS_API_KEY")

# --- 1. FUNÇÃO PARA OBTER O TOKEN DE ACESSO (BEARER TOKEN) - VERSÃO CORRIGIDA ---
def get_access_token(basic_token):
    """
    Usa a chave Basic para se autenticar no servidor de autenticação
    e obter um token de acesso temporário (Bearer Token), especificando o "audience".
    """
    auth_url = "https://auth.kpler.com/oauth/token" # Endpoint de autenticação
    
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # --- CORREÇÃO FINAL: Adicionar o parâmetro "audience" ---
    payload = {
        "grant_type": "client_credentials",
        "audience": "https://api.kpler.com"  # Especifica para qual API queremos o token
    }
    # --------------------------------------------------------
    
    print("🔑 Obtendo token de acesso (Bearer Token )...")
    try:
        response = requests.post(auth_url, headers=headers, data=payload)
        
        if response.status_code == 200:
            access_token = response.json().get("access_token")
            print("  ✅  Token de acesso obtido com sucesso!")
            return access_token
        else:
            print(f"  ❌  Falha ao obter token de acesso: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"  ❌  Exceção ao obter token de acesso: {e}")
        return None

# --- 2. FUNÇÃO PARA BUSCAR DADOS USANDO O BEARER TOKEN ---
def fetch_ais_data(access_token, imo_list, buffer_time=1):
    """
    Busca os dados de AIS usando o Bearer Token de acesso.
    """
    url_template = "https://api.kpler.com/v2/ais"
    
    headers = {
        "Authorization": f"Bearer {access_token}" # Usa o token de acesso temporário
    }

    all_ais_data = []

    print(f"\nIniciando busca de dados para {len(imo_list )} navios...")
    for idx, imo in enumerate(imo_list, start=1):
        print(f"  [{idx}/{len(imo_list)}] Buscando dados para o IMO: {imo}")
        params = {"imo": imo}
        
        try:
            response = requests.get(url_template, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and isinstance(data["data"], list) and data["data"]:
                    all_ais_data.extend(data["data"])
                    print(f"  ✅  Sucesso! {len(data['data'])} registro(s) recebido(s) para o IMO {imo}.")
                else:
                    print(f"  ⚠️  Sucesso, mas nenhum dado retornado para o IMO {imo}")
            else:
                print(f"  ❌  Falha na requisição para o IMO {imo}: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"  ❌  Ocorreu uma exceção para o IMO {imo}: {e}")

        if idx < len(imo_list):
            time.sleep(buffer_time)

    if all_ais_data:
        return pd.DataFrame(all_ais_data)
    else:
        print("\n⚠️ Nenhum dado de AIS foi coletado.")
        return pd.DataFrame()

# --- PONTO DE ENTRADA PRINCIPAL DO SCRIPT ---
def main():
    """
    Função principal que orquestra o pipeline de dados para a PoC.
    """
    print("🚀 Iniciando Pipeline de Dados Kpler para a PoC...")
    
    if not BASIC_AUTH_TOKEN or "SUA_CHAVE" in BASIC_AUTH_TOKEN:
        print("\n❌ ERRO: Chave de API (Basic Token) não encontrada no arquivo .env.")
        print("Por favor, gere uma nova chave no site da Kpler e adicione-a ao arquivo .env.")
        return

    # Passo 1: Obter o token de acesso
    access_token = get_access_token(BASIC_AUTH_TOKEN)
    
    if not access_token:
        print("\nPipeline interrompido. Não foi possível obter o token de acesso.")
        return

    # Passo 2: Usar o token de acesso para buscar os dados
    imo_list_poc = [9811000, 9839172, 9863297, 9462757, 9780882] 
    print(f"Monitorando {len(imo_list_poc)} navios: {imo_list_poc}")
    
    df_ais = fetch_ais_data(access_token, imo_list_poc)

    if df_ais.empty:
        print("\nPipeline concluído, mas nenhum dado foi salvo.")
        return

    print(f"\n✅ Sucesso! {len(df_ais)} registros de posição foram coletados.")
    output_filename = "poc_dados_frota.csv"
    df_ais.to_csv(output_filename, index=False)
    print(f"\n💾 Dados salvos com sucesso em: {output_filename}")
    print("\nPipeline concluído.")

if __name__ == "__main__":
    main()
