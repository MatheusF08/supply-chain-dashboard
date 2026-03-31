# dashboard.py - VERSÃO FINAL COM AUTENTICAÇÃO

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SEÇÃO DE AUTENTICAÇÃO
# -----------------------------------------------------------------------------

def check_password():
    """Retorna True se o usuário estiver autenticado, False caso contrário."""
    
    # Função interna para ser chamada quando a senha for digitada
    def password_entered():
        """Verifica se a senha digitada corresponde à senha secreta."""
        # Compara a senha digitada com a senha armazenada nos "Secrets" do Streamlit
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove a senha da memória da sessão por segurança
        else:
            st.session_state["password_correct"] = False

    # Se o usuário já passou pela verificação de senha com sucesso, permite o acesso
    if st.session_state.get("password_correct", False):
        return True

    # Layout do formulário de login no centro da página
    st.title("🚢 Central de Inteligência Marítima")
    st.write("Por favor, faça o login para continuar.")
    
    # Usando colunas para centralizar o formulário
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            submitted = st.form_submit_button("Entrar")
            
            if submitted:
                password_entered() # Chama a verificação quando o botão é clicado

    # Mostra mensagem de erro se a tentativa de login falhou
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuário ou senha incorretos.")
    
    # Se não estiver autenticado, retorna False e impede o resto do app de carregar
    return False

# -----------------------------------------------------------------------------
# 2. INÍCIO DA APLICAÇÃO PRINCIPAL
# -----------------------------------------------------------------------------

# Configuração da página (deve ser a primeira chamada do Streamlit)
st.set_page_config(
    page_title="Central de Inteligência Marítima",
    page_icon="🚢",
    layout="wide"
)

# --- VERIFICA A SENHA ---
# Se a função check_password() retornar False, o app para aqui.
if not check_password():
    st.stop()

# --- SE O LOGIN FOR BEM-SUCEDIDO, O CÓDIGO ABAIXO É EXECUTADO ---

# --- Título e Boas-Vindas ---
st.title("🚢 Central de Inteligência Marítima")
st.markdown(f"Bem-vindo, **{st.session_state.get('username', 'Usuário')}**!")

# --- Carregamento e Preparação dos Dados ---
# Usaremos os dados MOCK para o deploy inicial
DATA_FILE = "mock_dados_frota.csv"

@st.cache_data # Usa cache para não recarregar os dados a cada interação
def carregar_dados():
    if not os.path.exists(DATA_FILE):
        return None
    df = pd.read_csv(DATA_FILE)
    # Converte todas as colunas de data que podem existir
    for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em', 'TIMESTAMP']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

df = carregar_dados()

if df is None:
    st.error(f"Arquivo de dados '{DATA_FILE}' não encontrado.")
    st.warning("Certifique-se de que o arquivo de dados MOCK está no repositório do GitHub.")
    st.stop()

# --- Barra Lateral com Filtros ---
st.sidebar.header("Filtros Interativos")
status_selecionado = st.sidebar.multiselect(
    "Filtrar por Status do Navio:",
    options=df['Status do Navio'].unique(),
    default=df['Status do Navio'].unique()
)

disponibilidade_selecionada = st.sidebar.multiselect(
    "Filtrar por Disponibilidade:",
    options=df['Disponibilidade'].unique(),
    default=df['Disponibilidade'].unique()
)

# Aplica os filtros no dataframe
df_filtrado = df[
    df['Status do Navio'].isin(status_selecionado) &
    df['Disponibilidade'].isin(disponibilidade_selecionada)
]

# --- KPIs Principais ---
st.markdown("### Visão Geral da Frota Filtrada")
col1, col2, col3 = st.columns(3)
col1.metric("Navios na Seleção", f"{len(df_filtrado)}")
col2.metric("Navios Contratados", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Contratado'])}")
col3.metric("Navios Disponíveis", f"{len(df_filtrado[df_filtrado['Disponibilidade'] == 'Disponível para Frete'])}")

st.markdown("---")

# --- Criação das Abas (Tabs) ---
tab_cards, tab_tabela, tab_graficos = st.tabs([
    "Visão Geral (Cards)", 
    "Análise Detalhada (Tabela)", 
    "Gráficos Interativos"
])

# --- Aba 1: Visão Geral (Cards) ---
with tab_cards:
    st.header("Status Individual dos Navios")
    
    df_ordenado_cards = df_filtrado.sort_values(by="ETA Previsto")

    if df_ordenado_cards.empty:
        st.warning("Nenhum navio corresponde aos filtros selecionados.")
    else:
        for index, row in df_ordenado_cards.iterrows():
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

# --- Aba 2: Análise Detalhada (Tabela) ---
with tab_tabela:
    st.header("Dados Completos da Frota")
    st.markdown("Clique nos cabeçalhos das colunas para ordenar os dados.")
    
    # Prepara um dataframe para exibição com datas formatadas
    df_tabela = df_filtrado.copy()
    for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em', 'TIMESTAMP']:
        if col in df_tabela.columns:
            df_tabela[col] = df_tabela[col].dt.strftime('%d/%m/%Y %H:%M')
        
    st.dataframe(df_tabela, use_container_width=True)

# --- Aba 3: Gráficos Interativos ---
with tab_graficos:
    st.header("Análises Visuais da Frota Selecionada")

    if df_filtrado.empty:
        st.warning("Nenhum dado para exibir nos gráficos com os filtros atuais.")
    else:
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.subheader("Contagem de Navios por Status")
            fig_status = px.pie(
                df_filtrado, 
                names='Status do Navio', 
                title='Distribuição por Status',
                hole=.3
            )
            fig_status.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_status, use_container_width=True)

        with col_g2:
            st.subheader("Contagem de Navios por Porto")
            portos_counts = df_filtrado['Porto de Destino'].value_counts().reset_index()
            portos_counts.columns = ['Porto de Destino', 'Contagem']
            fig_portos = px.bar(
                portos_counts, 
                x='Porto de Destino', 
                y='Contagem',
                title='Navios por Porto de Destino',
                text_auto=True
            )
            st.plotly_chart(fig_portos, use_container_width=True)

        st.subheader("Linha do Tempo de Chegadas (ETA)")
        df_filtrado_sorted = df_filtrado.sort_values('ETA Previsto')
        fig_timeline = px.timeline(
            df_filtrado_sorted,
            x_start="ETA Previsto",
            x_end="Próxima Partida Estimada",
            y="Nome do Navio",
            color="Status do Navio",
            title="Linha do Tempo de Atividades dos Navios"
        )
        fig_timeline.update_yaxes(autorange="reversed") # Navios no topo chegam primeiro
        st.plotly_chart(fig_timeline, use_container_width=True)

