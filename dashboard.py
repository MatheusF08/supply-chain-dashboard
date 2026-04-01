# dashboard.py - VERSÃO COM DADOS REAIS (POC), DATAS RELATIVAS E LOGOUT

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime, timedelta

# Importa as classes da nossa arquitetura
try:
    from services.vessel_service import VesselService
    from providers.marinetraffic_provider import MarineTrafficProvider
except ImportError:
    class VesselService:
        def __init__(self, provider): pass
        def find_vessels_by_port(self, port_name): return pd.DataFrame()
    class MarineTrafficProvider:
        def __init__(self, api_key): pass

# -----------------------------------------------------------------------------
# 1. SEÇÃO DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    st.title("🚢 Central de Inteligência Marítima")
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            st.header("Login")
            username = st.text_input("Usuário", key="username")
            password = st.text_input("Senha", type="password", key="password")
            submitted = st.form_submit_button("Entrar")
            if submitted:
                if (st.session_state.get("username") == st.secrets.get("username") and
                    st.session_state.get("password") == st.secrets.get("password")):
                    st.session_state["password_correct"] = True
                else:
                    st.session_state["password_correct"] = False
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuário ou senha incorretos.")
    return False

# -----------------------------------------------------------------------------
# 2. FUNÇÕES DE DADOS E PREPARAÇÃO
# -----------------------------------------------------------------------------

def formatar_data_relativa(dt):
    """Formata uma data para um formato relativo (ex: 'há 2 horas')."""
    if pd.isna(dt):
        return "desconhecido"
    agora = datetime.now(dt.tz) # Garante que estamos comparando com o mesmo timezone
    diferenca = agora - dt
    segundos = diferenca.total_seconds()
    if segundos < 60:
        return "agora mesmo"
    minutos = round(segundos / 60)
    if minutos < 60:
        return f"há {minutos} min"
    horas = round(minutos / 60)
    if horas < 24:
        return f"há {horas}h"
    dias = round(horas / 24)
    return f"há {dias} dias"

@st.cache_data
def carregar_dados_frota(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): return None
    df = pd.read_csv(caminho_arquivo)
    for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em']:
        if col in df.columns:
            # Converte para datetime com timezone UTC, que é o padrão do GitHub Actions
            df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
    return df

@st.cache_data
def carregar_lista_de_portos(caminho_arquivo):
    """Carrega uma lista de portos para o autocomplete."""
    df_frota = carregar_dados_frota(caminho_arquivo)
    if df_frota is not None and 'Porto de Destino' in df_frota.columns:
        return sorted(df_frota['Porto de Destino'].unique().tolist())
    return ["Santos", "Paranaguá", "Rio Grande", "Itajaí", "Navegantes", "Suape", "Pecém", "Manaus"]

# -----------------------------------------------------------------------------
# 3. INÍCIO DA APLICAÇÃO PRINCIPAL
# -----------------------------------------------------------------------------

st.set_page_config(page_title="Central de Inteligência Marítima", page_icon="🚢", layout="wide")

if not check_password():
    st.stop()

# --- BARRA LATERAL COM LOGOUT ---
st.sidebar.header(f"Bem-vindo, {st.session_state.get('username', 'Usuário')}!")
if st.sidebar.button("Sair (Logout)"):
    st.session_state["password_correct"] = False
    if "username" in st.session_state: del st.session_state["username"]
    if "password" in st.session_state: del st.session_state["password"]
    st.rerun()
st.sidebar.markdown("---")

st.title("🚢 Central de Inteligência Marítima")

# --- MUDANÇA PRINCIPAL: USANDO O ARQUIVO DE DADOS REAIS (POC) ---
DATA_FILE_FROTA = "poc_dados_frota.csv"
df_frota = carregar_dados_frota(DATA_FILE_FROTA)
lista_portos = carregar_lista_de_portos(DATA_FILE_FROTA)

tab_monitoramento, tab_exploracao = st.tabs(["📍 Monitoramento de Frota", "🌍 Exploração Global"])

# -----------------------------------------------------------------------------
# ABA 1: MONITORAMENTO DE FROTA (COM DATAS RELATIVAS)
# -----------------------------------------------------------------------------
with tab_monitoramento:
    st.header("Monitoramento da Frota Estratégica")
    if df_frota is None:
        st.error(f"Arquivo de dados da frota '{DATA_FILE_FROTA}' não encontrado.")
        st.warning("O robô do GitHub Actions pode ainda não ter rodado. Verifique a aba 'Actions' no seu repositório.")
    else:
        st.sidebar.header("Filtros da Frota")
        status_selecionado = st.sidebar.multiselect("Filtrar por Status:", options=df_frota['Status do Navio'].unique(), default=df_frota['Status do Navio'].unique())
        disponibilidade_selecionada = st.sidebar.multiselect("Filtrar por Disponibilidade:", options=df_frota['Disponibilidade'].unique(), default=df_frota['Disponibilidade'].unique())
        df_filtrado = df_frota[df_frota['Status do Navio'].isin(status_selecionado) & df_frota['Disponibilidade'].isin(disponibilidade_selecionada)]
        
        st.markdown("#### Visão Geral da Frota Filtrada")
        col1, col2, col3 = st.columns(3)
        col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
        col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
        col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")
        st.markdown("---")

        sub_tab_cards, sub_tab_tabela, sub_tab_graficos = st.tabs(["Visão Rápida (Cards)", "Análise Detalhada (Tabela)", "Gráficos Interativos"])
        with sub_tab_cards:
            st.subheader("Status Individual dos Navios")
            if df_filtrado.empty: st.warning("Nenhum navio corresponde aos filtros selecionados.")
            else:
                for _, row in df_filtrado.sort_values(by="ETA Previsto").iterrows():
                    status_color = {"Em Rota": "blue", "Ancorado": "orange", "Atracado": "green"}.get(row['Status do Navio'], "gray")
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1: st.subheader(f"{row['Nome do Navio']} (IMO: {row['IMO']})")
                        with c2: st.markdown(f"**<p style='text-align: right; color: {status_color};'>{row['Status do Navio']}</p>**", unsafe_allow_html=True)
                        
                        # --- MUDANÇA: USANDO A DATA RELATIVA ---
                        tempo_consulta = formatar_data_relativa(row['Consulta em'])
                        st.caption(f"Última atualização: {tempo_consulta}")
                        
                        ci1, ci2, ci3 = st.columns(3)
                        with ci1: st.info(f"Chegada: {row['ETA Previsto'].strftime('%d/%m %H:%M') if pd.notna(row['ETA Previsto']) else 'N/A'}")
                        with ci2: st.info(f"Destino: {row['Porto de Destino']}")
                        with ci3: st.info(f"Partida: {row['Próxima Partida Estimada'].strftime('%d/%m %H:%M') if pd.notna(row['Próxima Partida Estimada']) else 'N/A'}")
                        
                        cc1, cc2 = st.columns(2)
                        with cc1: st.success(f"Carga: {row['Carga Atual']}")
                        with cc2: st.warning(f"Disponibilidade: {row['Disponibilidade']}")
        with sub_tab_tabela:
            st.subheader("Dados Completos da Frota")
            df_tabela = df_filtrado.copy()
            for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em']:
                if col in df_tabela.columns: df_tabela[col] = df_tabela[col].dt.strftime('%d/%m/%Y %H:%M')
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
            else: st.warning("Nenhum dado para exibir nos gráficos com os filtros atuais.")

# -----------------------------------------------------------------------------
# ABA 2: EXPLORAÇÃO GLOBAL
# -----------------------------------------------------------------------------
with tab_exploracao:
    st.header("🔎 Encontre Navios por Porto")
    st.write("Use esta ferramenta para análises de mercado, concorrência ou para encontrar navios em locais específicos.")
    porto_selecionado = st.selectbox("Selecione um porto para buscar navios automaticamente:", options=lista_portos, index=None, placeholder="Selecione ou digite o nome do porto...")
    if porto_selecionado:
        with st.spinner(f"Buscando navios em '{porto_selecionado}'... (usando simulação)"):
            api_key = st.secrets.get("MARINETRAFFIC_API_KEY", "chave_mock_para_teste")
            provider = MarineTrafficProvider(api_key=api_key)
            service = VesselService(provider)
            df_resultados_porto = service.find_vessels_by_port(porto_selecionado)
        if df_resultados_porto.empty:
            st.error(f"Nenhum navio encontrado para '{porto_selecionado}' nos dados de simulação.")
        else:
            st.success(f"{len(df_resultados_porto)} navios encontrados para '{porto_selecionado}':")
            st.dataframe(df_resultados_porto, use_container_width=True)
            df_mapa = df_resultados_porto.copy()
            if 'LAT' in df_mapa.columns and 'LON' in df_mapa.columns:
                df_mapa.rename(columns={"LAT": "lat", "LON": "lon"}, inplace=True)
                st.subheader("Localização no Mapa")
                st.map(df_mapa)
