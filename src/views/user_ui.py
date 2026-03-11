import streamlit as st
from src.security.vault import sanitizar_prompt, detokenizar_resposta
from src.finops.billing import obter_limite_usuario, calcular_custo, obter_cache, guardar_cache
from src.services.llm_api import conectar_api_gemini
from src.security.auth import registar_log

def tela_usuario():
    email = st.session_state.current_user
    st.title("AegisLLM - Terminal Seguro")
    
    if email not in st.session_state.finops["gastos_usuarios"]:
        st.session_state.finops["gastos_usuarios"][email] = 0.0
    if email not in st.session_state.chat_history:
        st.session_state.chat_history[email] = []

    gasto_atual = st.session_state.finops["gastos_usuarios"][email]
    limite_atual = obter_limite_usuario(email)
    saldo = limite_atual - gasto_atual
    
    bloqueado = saldo < 0.001

    st.progress(min(gasto_atual/limite_atual, 1.0) if limite_atual > 0 else 0, text=f"Consumo: ${gasto_atual:.4f} / ${limite_atual:.4f}")

    if bloqueado:
        st.error(f"Orçamento insuficiente (${saldo:.4f}).")
        if email not in st.session_state.finops["solicitacoes_limite"]:
            if st.button("Pedir Aumento"):
                st.session_state.finops["solicitacoes_limite"].append(email)
                registar_log(email, "Alerta FinOps", "Ficou sem limite e pediu aumento")
                st.rerun()
    
    st.divider()
    
    for msg in st.session_state.chat_history[email]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    prompt = st.chat_input("Digite aqui...", disabled=bloqueado)
    
    if prompt:
        st.session_state.chat_history[email].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        p_sani, pii = sanitizar_prompt(prompt, email)
        if pii: st.toast("Dados sensíveis tokenizados!")

        custo_estimado_input = calcular_custo(p_sani, "")
        if (gasto_atual + custo_estimado_input) > limite_atual:
            st.error(f"O tamanho do texto inserido (estimativa: ${custo_estimado_input:.4f}) ultrapassa o seu saldo restante (${saldo:.4f}).")
            st.stop()
            
        resposta_ia = obter_cache(p_sani)
        
        with st.chat_message("assistant"):
            if resposta_ia:
                msg_ai = f" *Cache Semântico ($0.00)*\n\n---\n\n{resposta_ia}"
                st.markdown(msg_ai)
                registar_log(email, "Poupança FinOps", "Cache Semântico utilizado")
            else:
                with st.spinner("IA processando..."):
                    resp_bruta = conectar_api_gemini(p_sani)
                    resp_final = detokenizar_resposta(resp_bruta)
                    
                    custo = calcular_custo(p_sani, resp_bruta)
                    st.session_state.finops["gastos_usuarios"][email] += custo
                    st.session_state.finops["gasto_total"] += custo
                    
                    guardar_cache(p_sani, resp_final)
                    
                    msg_ai = f"*Custo: ${custo:.4f}* | *Visão IA:* `{p_sani}`\n\n---\n\n{resp_final}"
                    st.markdown(msg_ai)

        st.session_state.chat_history[email].append({"role": "assistant", "content": msg_ai})
        st.rerun()