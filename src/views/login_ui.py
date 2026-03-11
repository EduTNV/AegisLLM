import streamlit as st
from src.security.auth import verificar_senha

def tela_login():
    st.title("🛡️ AegisLLM - Login")
    with st.form("l"):
        e = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if verificar_senha(e, p):
                st.session_state.logged_in = True
                st.session_state.current_user = e
                st.session_state.current_role = st.session_state.db_users[e]["role"]
                st.rerun()
            else: 
                st.error("Credenciais inválidas.")
    