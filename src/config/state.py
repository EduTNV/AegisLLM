import streamlit as st
from src.config.settings import ADMIN_EMAIL
from src.security.auth import gerar_hash

def init_session_state():
    if "db_users" not in st.session_state:
        st.session_state.db_users = {
            ADMIN_EMAIL: {"hash": gerar_hash("admin123"), "role": "admin"},
            "joao@empresa.com": {"hash": gerar_hash("user123"), "role": "user"},
            "maria@empresa.com": {"hash": gerar_hash("user123"), "role": "user"}
        }

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_role = None

    if "finops" not in st.session_state:
        st.session_state.finops = {
            "limite_diario_global": 0.10, 
            "gasto_total": 0.0,
            "limites_absolutos": {}, 
            "gastos_usuarios": {},
            "solicitacoes_limite": []     
        }

    if "semantic_cache" not in st.session_state:
        st.session_state.semantic_cache = {}

    if "audit_logs" not in st.session_state:
        st.session_state.audit_logs = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if "token_vault" not in st.session_state:
        st.session_state.token_vault = {}