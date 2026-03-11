import streamlit as st
import hashlib
import re
import time
import math
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

# Configuração de Segurança de Ambiente
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)

# ==========================================
# 1. CONFIGURAÇÕES E ESTADO (SESSION STATE)
# ==========================================
st.set_page_config(page_title="AegisLLM", page_icon="🛡️", layout="wide")

ADMIN_EMAIL = "admin@empresa.com"
MOCK_SALT = b'super_secret_salt_for_poc' 

def gerar_hash(senha: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', senha.encode(), MOCK_SALT, 100000).hex()

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

# ==========================================
# 2. FUNÇÕES CORE (SEGURANÇA E IA)
# ==========================================
def registar_log(utilizador: str, evento: str, detalhes: str):
    st.session_state.audit_logs.append({
        "Data/Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Usuário": utilizador,
        "Evento": evento,
        "Detalhes": detalhes
    })

def verificar_senha(email: str, senha_plana: str) -> bool:
    if email in st.session_state.db_users:
        if st.session_state.db_users[email]["hash"] == gerar_hash(senha_plana):
            registar_log(email, "Login", "Autenticação bem-sucedida")
            return True
    return False

def sanitizar_prompt(texto: str, utilizador: str) -> tuple[str, list]:
    regex_regras = {
        "CPF": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "CARTAO": r"\b(?:\d[ -]*?){13,16}\b"
    }
    texto_limpo = texto
    dados_expostos = []
    
    for tipo, padrao in regex_regras.items():
        matches = re.findall(padrao, texto_limpo)
        for match in matches:
            if tipo not in dados_expostos:
                dados_expostos.append(tipo)
            token_id = hashlib.md5(match.encode()).hexdigest()[:6].upper()
            token_seguro = f"[{tipo}_TKN_{token_id}]"
            st.session_state.token_vault[token_seguro] = match
            texto_limpo = texto_limpo.replace(match, token_seguro)
            
    return texto_limpo, dados_expostos

def detokenizar_resposta(texto: str) -> str:
    texto_restaurado = texto
    for token, dado_real in st.session_state.token_vault.items():
        if token in texto_restaurado:
            texto_restaurado = texto_restaurado.replace(token, f"**{dado_real}**")
    return texto_restaurado

def obter_limite_usuario(email: str) -> float:
    return st.session_state.finops["limites_absolutos"].get(email, st.session_state.finops["limite_diario_global"])

def calcular_custo(texto_in: str, texto_out: str) -> float:
    tokens_in = math.ceil(len(texto_in) / 4)
    tokens_out = math.ceil(len(texto_out) / 4)
    custo = ((tokens_in / 1000) * 0.001) + ((tokens_out / 1000) * 0.002)
    return max(custo, 0.015)

def obter_cache(prompt_sanitizado: str) -> str:
    prompt_hash = hashlib.md5(prompt_sanitizado.strip().lower().encode()).hexdigest()
    return st.session_state.semantic_cache.get(prompt_hash)

def guardar_cache(prompt_sanitizado: str, resposta: str):
    prompt_hash = hashlib.md5(prompt_sanitizado.strip().lower().encode()).hexdigest()
    st.session_state.semantic_cache[prompt_hash] = resposta

def conectar_api_gemini(prompt_sanitizado: str) -> str:
    if not GEMINI_API_KEY:
        return f"⚠️ [MODO MOCK] IA recebeu: {prompt_sanitizado}\n\nO sistema está operando sem API KEY real."
    try:
        instrucao = (
            "Você é o núcleo de inteligência do nosso Safe Gateway Corporativo. "
            "Ao encontrar tokens como [CPF_TKN_...], entenda que são dados reais protegidos. "
            "Responda normalmente como se tivesse acesso ao banco de dados, citando o token "
            "no contexto da sua análise."
        )
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=instrucao)
        response = model.generate_content(prompt_sanitizado)
        return response.text
    except Exception as e:
        return f"❌ Erro na API: {str(e)}"

# ==========================================
# 3. INTERFACES (UI)
# ==========================================
def tela_admin():
    st.title("⚙️ Painel de Controle de Governação (Admin)")
    
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
        if st.button("Aplicar Limite Individual"):
            st.session_state.finops["limites_absolutos"][target] = u_lim
            st.success(f"Limite de {target} fixado em ${u_lim}!")
            
        # FIX: Restaurada a seção de aprovações do Admin
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

def tela_usuario():
    email = st.session_state.current_user
    st.title("Terminal de IA Corporativo")
    
    if email not in st.session_state.finops["gastos_usuarios"]:
        st.session_state.finops["gastos_usuarios"][email] = 0.0
    if email not in st.session_state.chat_history:
        st.session_state.chat_history[email] = []

    gasto_atual = st.session_state.finops["gastos_usuarios"][email]
    limite_atual = obter_limite_usuario(email)
    saldo = limite_atual - gasto_atual
    
    bloqueado = saldo < 0.015

    st.progress(min(gasto_atual/limite_atual, 1.0) if limite_atual > 0 else 0, text=f"Consumo: ${gasto_atual:.4f} / ${limite_atual:.4f}")

    if bloqueado:
        st.error(f"⚠️ Orçamento insuficiente (${saldo:.4f}).")
        if email not in st.session_state.finops["solicitacoes_limite"]:
            if st.button("Pedir Aumento"):
                st.session_state.finops["solicitacoes_limite"].append(email)
                st.rerun()
    
    st.divider()
    
    for msg in st.session_state.chat_history[email]:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    prompt = st.chat_input("Digite aqui...", disabled=bloqueado)
    
    if prompt:
        st.session_state.chat_history[email].append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        p_sani, pii = sanitizar_prompt(prompt, email)
        if pii: st.toast("🛡️ Dados sensíveis tokenizados!")

        custo_estimado_input = calcular_custo(p_sani, "")
        if (gasto_atual + custo_estimado_input) > limite_atual:
            st.error(f"❌ O tamanho do texto inserido (estimativa: ${custo_estimado_input:.4f}) ultrapassa o seu saldo restante (${saldo:.4f}).")
            st.stop()
        # FIX: Restaurada a lógica de Cache Semântico
        resposta_ia = obter_cache(p_sani)
        
        with st.chat_message("assistant"):
            if resposta_ia:
                msg_ai = f"⚡ *Cache Semântico ($0.00)*\n\n---\n\n{resposta_ia}"
                st.markdown(msg_ai)
                registar_log(email, "Poupança FinOps", "Cache Semântico utilizado")
            else:
                with st.spinner("IA processando..."):
                    resp_bruta = conectar_api_gemini(p_sani)
                    resp_final = detokenizar_resposta(resp_bruta)
                    
                    # FIX: Restaurada a matemática real do FinOps
                    custo = calcular_custo(p_sani, resp_bruta)
                    st.session_state.finops["gastos_usuarios"][email] += custo
                    st.session_state.finops["gasto_total"] += custo
                    
                    guardar_cache(p_sani, resp_final)
                    
                    msg_ai = f"💰 *Custo: ${custo:.4f}* | 🛡️ *Visão IA:* `{p_sani}`\n\n---\n\n{resp_final}"
                    st.markdown(msg_ai)

        st.session_state.chat_history[email].append({"role": "assistant", "content": msg_ai})
        st.rerun()

def tela_login():
    st.title("🛡️ Login - AegisLLM")
    with st.form("l"):
        e = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if verificar_senha(e, p):
                st.session_state.logged_in = True
                st.session_state.current_user = e
                st.session_state.current_role = st.session_state.db_users[e]["role"]
                st.rerun()
            else: st.error("Erro")
    # FIX: Restaurado o Helper de Login
    st.info("Credenciais POC: admin@empresa.com / admin123 | joao@empresa.com / user123")

def main():
    if not st.session_state.logged_in: tela_login()
    else:
        with st.sidebar:
            st.write(f"Sessão: **{st.session_state.current_user}**")
            if st.button("Sair"):
                st.session_state.logged_in = False
                st.rerun()
        if st.session_state.current_role == "admin": tela_admin()
        else: tela_usuario()

if __name__ == "__main__": main()