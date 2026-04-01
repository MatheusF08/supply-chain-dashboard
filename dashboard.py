# dashboard.py (VERSÃO DE TESTE - ETAPA 1: PANDAS + DADOS PEQUENOS)

import streamlit as st
import pandas as pd # Adicionamos o pandas de volta
import os

# --- Funções de Autenticação e Carregamento ---
def check_password():
    if st.session_state.get("password_correct", False):
        return True
    st.title("🚢 Teste de Inicialização")
    with st.form("login_form"):
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        if st.form_submit_button("Entrar"):
            st.session_state["password_correct"] = True
            st.rerun()
    return False

@st.cache_data
def carregar_dados_frota(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): 
        return None
    df = pd.read_csv(caminho_arquivo)
    return df

# --- Aplicação Principal ---
st.set_page_config(page_title="Teste de Dashboard", layout="wide")

if not check_password():
    st.stop()

st.title("Etapa 1: Testando o Pandas")

# Tentamos carregar o arquivo pequeno
df_frota = carregar_dados_frota("poc_dados_frota.csv")

if df_frota is not None:
    st.success("✅ Sucesso! O Pandas foi importado e o arquivo 'poc_dados_frota.csv' foi carregado.")
    st.write("A aplicação consegue carregar um arquivo de dados pequeno sem problemas.")
    st.dataframe(df_frota)
else:
    st.error("❌ Falha! Não foi possível encontrar o arquivo 'poc_dados_frota.csv'.")

