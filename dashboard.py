# dashboard.py (VERSÃO DE TESTE - ETAPA 3: PLOTLY)

import streamlit as st
import pandas as pd
import os
import plotly.express as px # Adicionamos o Plotly de volta

# --- Funções ---
def check_password():
    # ... (código da função sem alteração)
    if st.session_state.get("password_correct", False): return True
    st.title("🚢 Teste de Inicialização")
    with st.form("login_form"):
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        if st.form_submit_button("Entrar"):
            st.session_state["password_correct"] = True
            st.rerun()
    return False

@st.cache_data
def carregar_dados_portuarios(caminho_arquivo):
    if not os.path.exists(caminho_arquivo): return None
    df = pd.read_csv(caminho_arquivo)
    for col in ['Chegada', 'Atracacao', 'Desatracacao']:
        if col in df.columns: df[col] = pd.to_datetime(df[col], errors='coerce')
    return df

# --- Aplicação Principal ---
st.set_page_config(page_title="Teste de Dashboard", layout="wide")

if not check_password():
    st.stop()

st.title("Etapa 3: Testando o Plotly")

df_portuario = carregar_dados_portuarios("dados_portuarios.csv")

if df_portuario is not None:
    st.success("✅ Arquivo carregado. Agora, tentando renderizar um gráfico Plotly...")
    
    try:
        df_portuario['Mes'] = df_portuario['Chegada'].dt.month
        tempo_medio_mes = df_portuario.groupby('Mes')['TempoEsperaAtracacao'].mean().reset_index()
        
        fig = px.bar(tempo_medio_mes, x='Mes', y='TempoEsperaAtracacao')
        
        st.plotly_chart(fig, use_container_width=True)
        st.success("✅ SUCESSO FINAL! O Plotly também funciona!")
        st.write("Se você está vendo isso, o problema original pode ter sido uma combinação de fatores que o 'Reboot' resolveu, ou a otimização do CSV foi suficiente.")
        st.write("Agora podemos montar a aplicação completa novamente, sabendo que as partes funcionam.")

    except Exception as e:
        st.error(f"❌ O PLOTLY QUEBROU! O erro foi: {e}")

else:
    st.error("❌ Falha! Não foi possível encontrar o arquivo 'dados_portuarios.csv'.")

