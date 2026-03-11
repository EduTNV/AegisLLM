# 🛡️ AegisLLM: Governance & FinOps Gateway

Uma Prova de Conceito (POC) de um Middleware inteligente posicionado entre usuários corporativos e LLMs (Large Language Models), focado em **Segurança de Dados (Privacy)** e **Controle de Custos (FinOps)**.

## 🚀 Funcionalidades Principais

- **Data Vault (Tokenização Reversível):** Intercepta dados sensíveis (CPF, E-mail, Cartões) e os substitui por tokens determinísticos antes do envio para a API externa. A resposta da IA é detokenizada em tempo real para o usuário final, garantindo 100% de privacidade sem perder o contexto.
- **FinOps Dashboard:** Gestão de orçamentos com "Shadow Billing" (simulação de custos reais de mercado) e travas preemptivas de limites diários globais e individuais.
- **Semantic Cache:** Sistema de cache baseado em hash criptográfico de prompts para evitar chamadas duplicadas à API, reduzindo custos a zero para requisições repetidas.
- **Trilha de Auditoria:** Registro completo de eventos de segurança, incluindo tentativas de vazamento de PII (Personally Identifiable Information).

## 🛠️ Stack Tecnológica

- **Linguagem:** Python 3.x
- **Interface:** Streamlit
- **Integração de IA:** Google Gemini 2.5 Flash API
- **Segurança:** PBKDF2 HMAC com SHA-256 (Hashing) e expressões regulares (Regex).

## 📦 Como Executar

### 1. Clone o repositório
```bash
git clone [https://github.com/seu-usuario/AegisLLM.git](https://github.com/seu-usuario/AegisLLM.git)
cd AegisLLM
2. Crie e ative seu ambiente virtual
No Windows:

Bash
python -m venv venv
.\venv\Scripts\activate
No Linux/Mac:

Bash
python3 -m venv venv
source venv/bin/activate
3. Instale as dependências
Bash
pip install -r requirements.txt
4. Configure as Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto e adicione a sua chave de API do Google Gemini:

Plaintext
GEMINI_API_KEY=sua_chave_aqui
(Nota: Certifique-se de que o arquivo .env esteja listado no seu .gitignore para não expor sua chave no GitHub).

5. Execute a aplicação
Bash
streamlit run gateway_poc.py
Desenvolvido por Eduardo Vital como estudo de caso prático de Governança de IA, Segurança e Engenharia de Software.