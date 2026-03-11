import google.generativeai as genai
from src.config.settings import GEMINI_API_KEY

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

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