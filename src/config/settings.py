import os
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_EMAIL = "admin@empresa.com"
MOCK_SALT = b'super_secret_salt_for_poc'