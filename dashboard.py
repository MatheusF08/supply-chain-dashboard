# dashboard.py - VERSÃO CORRIGIDA E COMPLETA COM TODAS AS FUNCIONALIDADES

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# Importa as classes da nossa arquitetura
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
                # Use st.secrets.get() para evitar erro se o secret não existir
                if st.secrets and st.session_state["password"] == st.secrets.get("password"):
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
# ABA 1: MONITORAMENTO DE FROTA (Versão completa com tudo)
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
        
        # --- KPIs ---
        st.markdown("### Visão Geral da Frota")
        col1, col2, col3 = st.columns(3)
        col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
        col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
        col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")
        
        st.markdown("---")

        # --- Sub-abas para organizar a visualização ---
        sub_tab_cards, sub_tab_tabela, sub_tab_graficos = st.tabs([
            "Visão por Cards", "Tabela Detalhada", "Análise Gráfica"
        ])

        with sub_tab_cards:
            st.subheader("Status Individual dos Navios")
            for index, row in df_filtrado.sort_values(by="ETA Previsto").iterrows():
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
            st.dataframe(df_filtrado, use_container_width=True)

        with sub_tab_graficos:
            st.subheader("Análises Visuais da Frota")
            if not df_filtrado.empty:
                g1, g2 = st.columns(2)
                with g1:
                    fig_status = px.pie(df_filtrado, names='Status do Navio', title='Distribuição por Status', hole=.3)
                    st.plotly_chart(fig_status, use_container_width=True)
                with g2:
                    fig_portos = px.bar(df_filtrado['Porto de Destino'].value_counts().reset_index(), x='Porto de Destino', y='count', title='Navios por Porto de Destino')
                    st.plotly_chart(fig_portos, use_container_width=True)
            else:
                st.warning("Nenhum dado para exibir nos gráficos com os filtros atuais.")


# ABA 2: EXPLORAÇÃO GLOBAL (Código NOVO com busca por "Enter")
with tab_exploracao:
    st.header("🔎 Encontre Navios por Porto")
    st.write("Use esta ferramenta para análises de mercado, concorrência ou para encontrar navios em locais específicos.")
    
    # --- INÍCIO DA MUDANÇA ---
    # Criamos um formulário que engloba o campo de texto e o botão
    with st.form(key="search_form"):
        porto_input = st.text_input(
            "Digite o nome de um porto e pressione Enter ou clique em Buscar", 
            key="porto_input"
        )
        
        # O botão agora é um "submit_button" do formulário
        submitted = st.form_submit_button("Buscar Navios no Porto")
    # --- FIM DA MUDANÇA ---

    # A lógica da busca agora é acionada se o formulário for submetido
    if submitted:
        if not porto_input:
            st.warning("Por favor, digite o nome de um porto.")
        else:
            with st.spinner(f"Buscando navios em '{porto_input}'... (usando simulação)"):
                api_key = st.secrets.get("MARINETRAFFIC_API_KEY", "chave_mock_para_teste")
                provider = MarineTrafficProvider(api_key=api_key)
                service = VesselService(provider)
                df_resultados_porto = service.find_vessels_by_port(porto_input)

            if df_resultados_porto.empty:
                st.error(f"Nenhum navio encontrado para '{porto_input}' nos dados de simulação.")
            else:
                st.success(f"{len(df_resultados_porto)} navios encontrados para '{porto_input}':")
                st.dataframe(df_resultados_porto, use_container_width=True)
                if 'LAT' in df_resultados_porto.columns and 'LON' in df_resultados_porto.columns:
                    st.subheader("Localização no Mapa")
                    df_mapa = df_resultados_porto.rename(columns={"LAT": "lat", "LON": "lon"})
                    st.map(df_mapa)

