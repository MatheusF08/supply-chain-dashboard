# dashboard.py - VERSÃO FINAL E FUNCIONAL COM DADOS OTIMIZADOS

import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

# --- Funções de Autenticação e Auxiliares ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    st.title("🚢 Central de Inteligência Marítima")
    st.write("")
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            st.header("Login")
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            if st.form_submit_button("Entrar"):
                if (st.session_state.get("username") == st.secrets.get("username") and
                    st.session_state.get("password") == st.secrets.get("password")):
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.session_state["password_correct"] = False
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Usuário ou senha incorretos.")
    return False

# --- Funções de Carregamento de Dados ---
@st.cache_data
def carregar_dados_frota(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): return None
    df = pd.read_csv(caminho_arquivo)
    for col in ['ETA Previsto', 'Próxima Partida Estimada', 'Consulta em']:
        if col in df.columns: df[col] = pd.to_datetime(df[col], utc=True, errors='coerce')
    return df

@st.cache_data
def carregar_lista_de_portos(caminho_arquivo):
    df_frota = carregar_dados_frota(caminho_arquivo)
    if df_frota is not None and 'Porto de Destino' in df_frota.columns:
        return sorted(df_frota['Porto de Destino'].unique().tolist())
    return ["Santos", "Paranaguá", "Rio Grande"]

@st.cache_data
def carregar_dados_portuarios(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): return None
    df = pd.read_csv(caminho_arquivo)
    for col in ['Chegada', 'Atracacao', 'Desatracacao']:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# -----------------------------------------------------------------------------
# INÍCIO DA APLICAÇÃO PRINCIPAL
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Central de Inteligência Marítima", page_icon="🚢", layout="wide")

if not check_password():
    st.stop()

st.sidebar.header(f"Bem-vindo, {st.session_state.get('username', 'Usuário')}!")
if st.sidebar.button("Sair (Logout)"):
    st.session_state["password_correct"] = False
    st.rerun()
st.sidebar.markdown("---")

st.title("🚢 Central de Inteligência Marítima")

df_frota = carregar_dados_frota("poc_dados_frota.csv")
df_portuario = carregar_dados_portuarios("dados_portuarios.csv") # Carrega a versão otimizada
lista_portos_poc = carregar_lista_de_portos("poc_dados_frota.csv") if df_frota is not None else []

tabs_disponiveis = ["📍 Monitoramento de Frota", "🌍 Exploração Global"]
if df_portuario is not None:
    tabs_disponiveis.append("📊 Análise Portuária (Brasil)")

tab_widgets = st.tabs(tabs_disponiveis)
tab_monitoramento = tab_widgets[0]
tab_exploracao = tab_widgets[1]
if df_portuario is not None:
    tab_analise_portuaria = tab_widgets[2]

with tab_monitoramento:
    st.header("Monitoramento da Frota Estratégica")
    if df_frota is None:
        st.error("Arquivo 'poc_dados_frota.csv' não encontrado.")
    else:
        st.sidebar.header("Filtros da Frota")
        status_selecionado = st.sidebar.multiselect("Filtrar por Status:", options=df_frota['Status do Navio'].unique(), default=df_frota['Status do Navio'].unique())
        disponibilidade_selecionada = st.sidebar.multiselect("Filtrar por Disponibilidade:", options=df_frota['Disponibilidade'].unique(), default=df_frota['Disponibilidade'].unique())
        df_filtrado = df_frota[df_frota['Status do Navio'].isin(status_selecionado) & df_frota['Disponibilidade'].isin(disponibilidade_selecionada)]
        # (Aqui entraria o resto do código da Aba 1: KPIs, cards, etc.)
        st.dataframe(df_filtrado)


with tab_exploracao:
    st.header("🔎 Encontre Navios por Porto")
    porto_selecionado = st.selectbox(
        "Selecione um porto para buscar navios (simulação):",
        options=lista_portos_poc,
        index=None,
        placeholder="Selecione ou digite o nome do porto..."
    )
    # (Aqui entraria o resto do código da Aba 2)
    if porto_selecionado:
        st.info(f"Simulação de busca para o porto: {porto_selecionado}")


if df_portuario is not None:
    with tab_analise_portuaria:
        st.header("Análise de Desempenho dos Portos Brasileiros")
        st.markdown("Fonte: Dados Abertos da ANTAQ (Ano de 2023)")

        st.sidebar.header("Filtros de Análise Portuária")
        
        portos_disponiveis = sorted(df_portuario['Porto'].unique())
        porto_selecionado_antaq = st.sidebar.selectbox(
            "Selecione um Porto:",
            options=portos_disponiveis,
            index=0 # Como só tem Santos, o índice 0 está bom
        )

        df_filtrado_antaq = df_portuario[df_portuario['Porto'] == porto_selecionado_antaq].copy()

        st.subheader(f"Desempenho do Porto de {porto_selecionado_antaq}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Tempo Médio de Espera (Atracação)", f"{df_filtrado_antaq['TempoEsperaAtracacao'].mean():.1f} horas")
        col2.metric("Tempo Médio Atracado", f"{df_filtrado_antaq['TempoAtracado'].mean():.1f} horas")
        col3.metric("Total de Atracações no Ano", f"{len(df_filtrado_antaq):,}".replace(",", "."))
        
        st.markdown("---")

        g1, g2 = st.columns(2)
        with g1:
            st.markdown("#### Tempo Médio de Espera por Mês")
            df_filtrado_antaq['Mes'] = df_filtrado_antaq['Chegada'].dt.month
            tempo_medio_mes = df_filtrado_antaq.groupby('Mes')['TempoEsperaAtracacao'].mean().reset_index()
            
            fig = px.bar(tempo_medio_mes, x='Mes', y='TempoEsperaAtracacao',
                         labels={'Mes': 'Mês', 'TempoEsperaAtracacao': 'Horas de Espera'}, text_auto='.1f')
            st.plotly_chart(fig, use_container_width=True)

        with g2:
            st.markdown("#### Top 5 Tipos de Navegação por No. de Atracações")
            navegacao_counts = df_filtrado_antaq['Navegacao'].value_counts().nlargest(5)
            fig2 = px.pie(navegacao_counts, values=navegacao_counts.values, names=navegacao_counts.index, hole=.3)
            st.plotly_chart(fig2, use_container_width=True)
