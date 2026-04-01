# dashboard.py (VERSÃO DE TESTE MÍNIMA)

import streamlit as st

# Sem Pandas, sem Plotly, sem carregar arquivos. Apenas Streamlit puro.

def check_password():
    """Função de login simplificada para teste."""
    if st.session_state.get("password_correct", False):
        return True

    st.title("🚢 Teste de Inicialização")
    with st.form("login_form"):
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        if st.form_submit_button("Entrar"):
            # Para este teste, qualquer login funciona.
            st.session_state["password_correct"] = True
            st.rerun()
    return False

st.set_page_config(page_title="Teste de Dashboard", layout="wide")

if not check_password():
    st.stop()

# Se o login funcionar, mostre apenas um título.
st.title("✅ Sucesso! A aplicação base está funcionando.")
st.balloons()

