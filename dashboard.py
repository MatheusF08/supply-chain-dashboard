# dashboard.py - VERSÃO FINAL COM EXPLORAÇÃO GLOBAL

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# Importa as classes da nossa nova arquitetura
from services.vessel_service import VesselService
from providers.marinetraffic_provider import MarineTrafficProvider

# -----------------------------------------------------------------------------
# 1. SEÇÃO DE AUTENTICAÇÃO (sem alterações)
# -----------------------------------------------------------------------------
def check_password():
    """Retorna True se o usuário estiver autenticado, False caso contrário."""
    if st.session_state.get("password_correct", False):
        return True
    
    st.title("🚢 Central de Inteligência Marítima")
    st.write("Por favor, faça o login para continuar.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                if st.session_state["password"] == st.secrets.get("password", "admin123"):
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.session_state["password_correct"] = False

    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuário ou senha incorretos.")
    
    return False

# -----------------------------------------------------------------------------
# 2. INÍCIO DA APLICAÇÃO PRINCIPAL
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Central de Inteligência Marítima",
    page_icon="🚢",
    layout="wide"
)

if not check_password():
    st.stop()

st.title("🚢 Central de Inteligência Marítima")
st.markdown(f"Bem-vindo, **{st.session_state.get('username', 'Usuário')}**!")

# --- Criação das Abas (Tabs) ---
tab_monitoramento, tab_exploracao = st.tabs([
    "📍 Monitoramento de Frota", 
    "🌍 Exploração Global"
])


# -----------------------------------------------------------------------------
# ABA 1: MONITORAMENTO DE FROTA (Nosso dashboard antigo)
# -----------------------------------------------------------------------------
with tab_monitoramento:
    st.header("Monitoramento da Frota Estratégica")
    
    DATA_FILE = "mock_dados_frota.csv"

    @st.cache_data
    def carregar_dados_frota():
        if not os.path.exists(DATA_FILE):
            return None
        df = pd.read_csv(DATA_FILE)
        for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em', 'TIMESTAMP']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df

    df_frota = carregar_dados_frota()

    if df_frota is None:
        st.error(f"Arquivo de dados da frota '{DATA_FILE}' não encontrado.")
        st.warning("Certifique-se de que o arquivo de dados MOCK está no repositório.")
    else:
        # --- Barra Lateral com Filtros ---
        st.sidebar.header("Filtros da Frota")
        status_selecionado = st.sidebar.multiselect(
            "Filtrar por Status:",
            options=df_frota['Status do Navio'].unique(),
            default=df_frota['Status do Navio'].unique(),
            key="filtro_status_frota"
        )
        disponibilidade_selecionada = st.sidebar.multiselect(
            "Filtrar por Disponibilidade:",
            options=df_frota['Disponibilidade'].unique(),
            default=df_frota['Disponibilidade'].unique(),
            key="filtro_disp_frota"
        )
        df_filtrado = df_frota[
            df_frota['Status do Navio'].isin(status_selecionado) &
            df_frota['Disponibilidade'].isin(disponibilidade_selecionada)
        ]
        
        # --- KPIs e Cards (código anterior) ---
        st.markdown("### Visão Geral da Frota")
        col1, col2, col3 = st.columns(3)
        col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
        col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
        col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")
        
        st.markdown("---")
        st.subheader("Status Individual dos Navios")
        for index, row in df_filtrado.sort_values(by="ETA Previsto").iterrows():
             with st.container(border=True):
                # ... (código dos cards que já tínhamos) ...
                st.text(f"{row['Nome do Navio']} (IMO: {row['IMO']}) - Destino: {row['Porto de Destino']}")


# -----------------------------------------------------------------------------
# ABA 2: EXPLORAÇÃO GLOBAL (Nova funcionalidade)
# -----------------------------------------------------------------------------
with tab_exploracao:
    st.header("🔎 Encontre Navios por Porto")
    st.write("Use esta ferramenta para análises de mercado, concorrência ou para encontrar navios em locais específicos.")
    
    porto_input = st.text_input("Digite o nome de um porto (ex: Santos, Roterdã, Xangai)", key="porto_input")
    
    if st.button("Buscar Navios no Porto", key="buscar_porto_btn"):
        if not porto_input:
            st.warning("Por favor, digite o nome de um porto.")
        else:
            with st.spinner(f"Buscando navios em '{porto_input}'... (usando simulação)"):
                # --- A MÁGICA ACONTECE AQUI ---
                # Inicializa o provedor e o serviço
                api_key = st.secrets.get("MARINETRAFFIC_API_KEY", "chave_mock_para_teste")
                provider = MarineTrafficProvider(api_key=api_key)
                service = VesselService(provider)
                
                # Chama a nova função do serviço
                df_resultados_porto = service.find_vessels_by_port(porto_input)
                # -----------------------------

            if df_resultados_porto.empty:
                st.error(f"Nenhum navio encontrado para '{porto_input}' nos dados de simulação.")
            else:
                st.success(f"{len(df_resultados_porto)} navios encontrados para '{porto_input}':")
                
                # Exibe os resultados em uma tabela
                st.dataframe(df_resultados_porto, use_container_width=True)

                # Opcional: Mostrar em um mapa se houver dados de lat/lon
                if 'LAT' in df_resultados_porto.columns and 'LON' in df_resultados_porto.columns:
                    st.subheader("Localização no Mapa")
                    df_mapa = df_resultados_porto.rename(columns={"LAT": "lat", "LON": "lon"})
                    st.map(df_mapa)

