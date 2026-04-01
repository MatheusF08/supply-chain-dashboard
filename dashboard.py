# dashboard.py - VERSÃO FINAL E COMPLETA

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta

# Importa as classes da nossa arquitetura
# O 'try/except' é uma boa prática para não quebrar o app se a estrutura de pastas mudar
try:
    from services.vessel_service import VesselService
    from providers.marinetraffic_provider import MarineTrafficProvider
except ImportError:
    # Se der erro na importação, definimos classes "dummy" para não quebrar o app
    # Isso é útil para depuração, mas o ideal é ter a estrutura de pastas correta
    class VesselService:
        def __init__(self, provider): pass
        def find_vessels_by_port(self, port_name): return pd.DataFrame()
    class MarineTrafficProvider:
        def __init__(self, api_key): pass

# -----------------------------------------------------------------------------
# 1. SEÇÃO DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def check_password():
    """Retorna True se o usuário estiver autenticado, False caso contrário."""
    
    def password_entered():
        """Verifica se o usuário e a senha digitados correspondem aos secrets."""
        # Usamos .get() para evitar erros se os secrets não estiverem configurados
        if st.session_state.get("username") == st.secrets.get("username") and st.session_state.get("password") == st.secrets.get("password"):
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Centraliza o formulário de login
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            # Adicionando um logo genérico para profissionalizar
            st.image("https://i.imgur.com/g0w5v9A.png", width=200 ) 
            st.header("Plataforma de Inteligência Marítima")
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                password_entered()
    
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

# --- Barra Lateral e Título Principal ---
st.sidebar.header(f"Bem-vindo, {st.session_state.get('username', 'Usuário')}!")
st.sidebar.markdown("---")
st.title("🚢 Central de Inteligência Marítima")

# --- Criação das Abas (Tabs) ---
tab_monitoramento, tab_exploracao = st.tabs([
    "📍 Monitoramento de Frota", 
    "🌍 Exploração Global"
])

# -----------------------------------------------------------------------------
# ABA 1: MONITORAMENTO DE FROTA (Versão completa com tudo)
# -----------------------------------------------------------------------------
with tab_monitoramento:
    st.header("Monitoramento da Frota Estratégica")
    
    DATA_FILE_FROTA = "mock_dados_frota.csv"

    @st.cache_data
    def carregar_dados_frota(caminho_arquivo):
        if not os.path.exists(caminho_arquivo):
            return None
        df = pd.read_csv(caminho_arquivo)
        for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        return df

    df_frota = carregar_dados_frota(DATA_FILE_FROTA)

    if df_frota is None:
        st.error(f"Arquivo de dados da frota '{DATA_FILE_FROTA}' não encontrado.")
        st.warning("Certifique-se de que o arquivo de dados MOCK está no repositório do GitHub.")
    else:
        # Filtros na barra lateral
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
        
        # KPIs
        st.markdown("#### Visão Geral da Frota Filtrada")
        col1, col2, col3 = st.columns(3)
        col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
        col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
        col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")
        st.markdown("---")

        # Sub-abas para organizar a visualização
        sub_tab_cards, sub_tab_tabela, sub_tab_graficos = st.tabs([
            "Visão Rápida (Cards)", "Análise Detalhada (Tabela)", "Gráficos Interativos"
        ])

        with sub_tab_cards:
            st.subheader("Status Individual dos Navios")
            if df_filtrado.empty:
                st.warning("Nenhum navio corresponde aos filtros selecionados.")
            else:
                for _, row in df_filtrado.sort_values(by="ETA Previsto").iterrows():
                    status_color = {"Em Rota": "blue", "Ancorado": "orange", "Atracado": "green"}.get(row['Status do Navio'], "gray")
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1: st.subheader(f"{row['Nome do Navio']} (IMO: {row['IMO']})")
                        with c2: st.markdown(f"**<p style='text-align: right; color: {status_color};'>{row['Status do Navio']}</p>**", unsafe_allow_html=True)
                        ci1, ci2, ci3 = st.columns(3)
                        with ci1: st.info(f"Chegada: {row['ETA Previsto'].strftime('%d/%m %H:%M')}")
                        with ci2: st.info(f"Destino: {row['Porto de Destino']}")
                        with ci3: st.info(f"Partida: {row['Próxima Partida Estimada'].strftime('%d/%m %H:%M')}")
                        cc1, cc2 = st.columns(2)
                        with cc1: st.success(f"Carga: {row['Carga Atual']}")
                        with cc2: st.warning(f"Disponibilidade: {row['Disponibilidade']}")

        with sub_tab_tabela:
            st.subheader("Dados Completos da Frota")
            df_tabela = df_filtrado.copy()
            for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em']:
                if col in df_tabela.columns:
                    df_tabela[col] = df_tabela[col].dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(df_tabela, use_container_width=True)

        with sub_tab_graficos:
            st.subheader("Análises Visuais da Frota")
            if not df_filtrado.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig_status = px.pie(df_filtrado, names='Status do Navio', title='Distribuição por Status', hole=.3)
                    st.plotly_chart(fig_status, use_container_width=True)
                with g2:
                    fig_portos = px.bar(df_filtrado['Porto de Destino'].value_counts().reset_index(), x='Porto de Destino', y='count', title='Navios por Porto de Destino', text_auto=True)
                    st.plotly_chart(fig_portos, use_container_width=True)
            else:
                st.warning("Nenhum dado para exibir nos gráficos com os filtros atuais.")

# -----------------------------------------------------------------------------
# ABA 2: EXPLORAÇÃO GLOBAL
# -----------------------------------------------------------------------------
with tab_exploracao:
    st.header("🔎 Encontre Navios por Porto")
    st.write("Use esta ferramenta para análises de mercado, concorrência ou para encontrar navios em locais específicos.")
    
    with st.form(key="search_form"):
        porto_input = st.text_input(
            "Digite o nome de um porto e pressione Enter ou clique em Buscar", 
            key="porto_input"
        )
        submitted = st.form_submit_button("Buscar Navios no Porto")

    if submitted:
        if not porto_input:
            st.warning("Por favor, digite o nome de um porto.")
        else:
            with st.spinner(f"Buscando navios em '{porto_input}'... (usando simulação)"):
                # Simula a chamada ao serviço, mesmo sem a chave real
                api_key = st.secrets.get("MARINETRAFFIC_API_KEY", "chave_mock_para_teste")
                provider = MarineTrafficProvider(api_key=api_key)
                service = VesselService(provider)
                df_resultados_porto = service.find_vessels_by_port(porto_input)

            if df_resultados_porto.empty:
                st.error(f"Nenhum navio encontrado para '{porto_input}' nos dados de simulação.")
            else:
                st.success(f"{len(df_resultados_porto)} navios encontrados para '{porto_input}':")
                st.dataframe(df_resultados_porto, use_container_width=True)
                
                # Renomeia colunas para o mapa e verifica se existem
                df_mapa = df_resultados_porto.copy()
                if 'LAT' in df_mapa.columns and 'LON' in df_mapa.columns:
                    df_mapa.rename(columns={"LAT": "lat", "LON": "lon"}, inplace=True)
                    st.subheader("Localização no Mapa")
                    st.map(df_mapa)
