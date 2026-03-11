import streamlit as st
import math
import hashlib

def obter_limite_usuario(email: str) -> float:
    return st.session_state.finops["limites_absolutos"].get(email, st.session_state.finops["limite_diario_global"])

def calcular_custo(texto_in: str, texto_out: str) -> float:
    tokens_in = math.ceil(len(texto_in) / 4)
    tokens_out = math.ceil(len(texto_out) / 4)
    custo = ((tokens_in / 1000) * 0.001) + ((tokens_out / 1000) * 0.002)
    return max(custo, 0.0001)

def obter_cache(prompt_sanitizado: str) -> str:
    prompt_hash = hashlib.md5(prompt_sanitizado.strip().lower().encode()).hexdigest()
    return st.session_state.semantic_cache.get(prompt_hash)

def guardar_cache(prompt_sanitizado: str, resposta: str):
    prompt_hash = hashlib.md5(prompt_sanitizado.strip().lower().encode()).hexdigest()
    st.session_state.semantic_cache[prompt_hash] = resposta