import streamlit as st
import hashlib
from datetime import datetime
from src.config.settings import MOCK_SALT

def gerar_hash(senha: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', senha.encode(), MOCK_SALT, 100000).hex()

def registar_log(usuario: str, evento: str, detalhes: str):
    st.session_state.audit_logs.append({
        "Data/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuário": usuario,
        "Evento": evento,
        "Detalhes": detalhes
    })

def verificar_senha(email: str, senha_plana: str) -> bool:
    if email in st.session_state.db_users:
        if st.session_state.db_users[email]["hash"] == gerar_hash(senha_plana):
            registar_log(email, "Login", "Autenticação bem-sucedida")
            return True
    return False