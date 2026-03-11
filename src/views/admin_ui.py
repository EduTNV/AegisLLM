import streamlit as st
import pandas as pd
from src.config.settings import ADMIN_EMAIL, GEMINI_API_KEY
from src.finops.billing import obter_limite_usuario
from src.security.auth import registar_log

def tela_admin():
    st.title("⚙️ AegisLLM - Painel de Controle (Admin)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Custo Total (FinOps)", f"${st.session_state.finops['gasto_total']:.4f}")
    col2.metric("Petições em Cache", len(st.session_state.semantic_cache))
    col3.metric("Itens no Cofre", len(st.session_state.token_vault))
    col4.metric("Status da API", "🟢" if GEMINI_API_KEY else "🔴")
    
    st.divider()
    
    c1, c2 = st.columns([2, 1.5])
    with c1:
        st.subheader("📊 Consumo")
        data = {u: st.session_state.finops["gastos_usuarios"].get(u, 0.0) for u in st.session_state.db_users if u != ADMIN_EMAIL}
        st.bar_chart(pd.Series(data))

    with c2:
        st.subheader("💰 Gestão de Orçamentos")
        g_lim = st.number_input("Limite Global ($)", value=float(st.session_state.finops["limite_diario_global"]), step=0.01, min_value=0.01)
        if st.button("Salvar Limite Global"):
            st.session_state.finops["limite_diario_global"] = g_lim
            st.success("Limite Global Atualizado!")

        st.markdown("---")
        u_list = [u for u in st.session_state.db_users if u != ADMIN_EMAIL]
        target = st.selectbox("Configurar Usuário Específico", u_list)
        u_lim = st.number_input(f"Orçamento para {target} ($)", value=float(obter_limite_usuario(target)), step=0.01, min_value=0.01)
        if st.button("Aplicar Limite Específico"):
            st.session_state.finops["limites_absolutos"][target] = u_lim
            st.success(f"Limite de {target} fixado em ${u_lim}!")
            
        st.markdown("---")
        st.subheader("Aprovações Pendentes")
        if not st.session_state.finops["solicitacoes_limite"]:
            st.caption("Nenhum pedido na fila.")
        for p_email in list(st.session_state.finops["solicitacoes_limite"]):
            if st.button(f"Aprovar +$0.10 para {p_email}", key=f"ap_{p_email}"):
                st.session_state.finops["limites_absolutos"][p_email] = obter_limite_usuario(p_email) + 0.10
                st.session_state.finops["solicitacoes_limite"].remove(p_email)
                registar_log(ADMIN_EMAIL, "Aprovação FinOps", f"Limite aumentado para {p_email}")
                st.rerun()

    st.subheader("📜 Logs de Auditoria")
    st.dataframe(pd.DataFrame(reversed(st.session_state.audit_logs)), use_container_width=True)