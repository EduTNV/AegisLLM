import streamlit as st
import re
import hashlib
from src.security.auth import registar_log

def sanitizar_prompt(texto: str, usuario: str) -> tuple[str, list]:
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