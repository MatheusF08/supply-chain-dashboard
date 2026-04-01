# dashboard.py - VERSÃO FINAL E COMPLETA (com Login Profissional)

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import base64  # Importado para o novo login
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
# 1. SEÇÃO DE AUTENTICAÇÃO (NOVA VERSÃO PROFISSIONAL)
# -----------------------------------------------------------------------------

@st.cache_data
def get_img_as_base64(file):
    """Função para carregar uma imagem local e converter para base64."""
    # Tenta carregar .jpg e depois .png
    if os.path.exists(file + ".jpg"):
        file_path = file + ".jpg"
    elif os.path.exists(file + ".png"):
        file_path = file + ".png"
    else:
        return None # Retorna None se nenhum dos formatos for encontrado
        
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def login_page():
    """Renderiza a página de login com fundo de imagem e formulário estilizado."""
    
    # Carrega a imagem de fundo (procura por 'background.jpg' ou 'background.png')
    img_base64 = get_img_as_base64("background")

    # Define o CSS para o background e o estilo do formulário
    background_style = f"""
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
    """ if img_base64 else "background-color: #1a1a2e;" # Cor de fundo fallback

    page_style = f"""
    <style>
    /* Aplica o estilo de fundo ao container principal */
    [data-testid="stAppViewContainer"] > .main {{
        {background_style}
    }}

    /* Esconde o header padrão do Streamlit na tela de login */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    /* Estilo para a caixa de login centralizada */
    .login-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: rgba(0, 0, 0, 0.75); /* Fundo preto semi-transparente */
        padding: 2rem 3rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        color: white;
        max-width: 450px;
        margin: auto; /* Centraliza a caixa */
    }}

    .login-box h1 {{
        color: white;
        text-align: center;
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
    }}
    
    /* Melhora a visibilidade dos inputs */
    .login-box .stTextInput > div > div > input {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }}
    
    /* Botão com mais destaque */
    .login-box .stButton > button {{
        width: 100%;
        border-radius: 5px;
        background-color: #0068C9; /* Azul padrão do Streamlit */
        color: white;
        font-weight: bold;
    }}
    </style>
    """
    st.markdown(page_style, unsafe_allow_html=True)
    
    if not img_base64:
        st.warning("Arquivo 'background.jpg' ou 'background.png' não encontrado. Usando cor de fundo padrão.")

    # Layout do formulário de login
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.image("https://i.imgur.com/g0w5v9A.png", width=150 ) # Logo
        st.markdown("<h1>Plataforma de Inteligência Marítima</h1>", unsafe_allow_html=True)
        
        username = st.text_input("Usuário", key="login_username", label_visibility="collapsed", placeholder="Usuário")
        password = st.text_input("Senha", type="password", key="login_password", label_visibility="collapsed", placeholder="Senha")
        
        if st.button("Entrar", key="login_button"):
            if username == st.secrets.get("username") and password == st.secrets.get("password"):
                st.session_state["authenticated"] = True
                st.session_state["username_display"] = username # Salva o nome para exibir depois
                st.rerun()
            else:
                st.error("😕 Usuário ou senha incorretos.")
        
        st.markdown('</div>', unsafe_allow_html=True)

def check_authentication():
    """Verifica se o usuário está autenticado. Se não, mostra a página de login."""
    if not st.session_state.get("authenticated", False):
        login_page()
        return False
    return True

# -----------------------------------------------------------------------------
# 2. INÍCIO DA APLICAÇÃO PRINCIPAL
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Central de Inteligência Marítima",
    page_icon="🚢",
    layout="wide"
)

if not check_authentication():
    st.stop()

# --- Barra Lateral e Título Principal ---
st.sidebar.header(f"Bem-vindo, {st.session_state.get('username_display', 'Usuário')}!")
st.sidebar.markdown("---")
st.title("🚢 Central de Inteligência Marítima")

# --- Criação das Abas (Tabs) ---
tab_monitoramento, tab_exploracao = st.tabs([
    "📍 Monitoramento de Frota", 
    "🌍 Exploração Global"
])

# -----------------------------------------------------------------------------
# ABA 1: MONITORAMENTO DE FROTA (Seu código original, sem alterações)
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
        
        st.markdown("#### Visão Geral da Frota Filtrada")
        col1, col2, col3 = st.columns(3)
        col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
        col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
        col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")
        st.markdown("---")

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
# ABA 2: EXPLORAÇÃO GLOBAL (Seu código original, sem alterações)
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
                api_key = st.secrets.get("MARINETRAFFIC_API_KEY", "chave_mock_para_teste")
                provider = MarineTrafficProvider(api_key=api_key)
                service = VesselService(provider)
                df_resultados_porto = service.find_vessels_by_port(porto_input)

            if df_resultados_porto.empty:
                st.error(f"Nenhum navio encontrado para '{porto_input}' nos dados de simulação.")
            else:
                st.success(f"{len(df_resultados_porto)} navios encontrados para '{porto_input}':")
                st.dataframe(df_resultados_porto, use_container_width=True)
                
                df_mapa = df_resultados_porto.copy()
                if 'LAT' in df_mapa.columns and 'LON' in df_mapa.columns:
                    df_mapa.rename(columns={"LAT": "lat", "LON": "lon"}, inplace=True)
                    st.subheader("Localização no Mapa")
                    st.map(df_mapa)
