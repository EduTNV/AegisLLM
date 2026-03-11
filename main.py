import streamlit as st

# Configuração da página deve ser a primeira chamada do Streamlit
st.set_page_config(page_title="AegisLLM Gateway", page_icon="🛡️", layout="wide")

from src.config.state import init_session_state
from src.views.login_ui import tela_login
from src.views.admin_ui import tela_admin
from src.views.user_ui import tela_usuario

def main():
    # Inicializa o banco de dados e variáveis de ambiente na sessão
    init_session_state()

    # Roteador de Telas (Router)
    if not st.session_state.logged_in:
        tela_login()
    else:
        with st.sidebar:
            st.write(f"Sessão: **{st.session_state.current_user}**")
            if st.button("Sair"):
                st.session_state.logged_in = False
                st.rerun()
                
        if st.session_state.current_role == "admin":
            tela_admin()
        else:
            tela_usuario()

if __name__ == "__main__":
    main()