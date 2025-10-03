import os
from decouple import config
from google.cloud import secretmanager

# --- Базовые настройки из переменных окружения ---
GCP_PROJECT_ID = config("GCP_PROJECT_ID")
GCP_REGION = config("GCP_REGION")
BUCKET_NAME = config("BUCKET_NAME")

# --- Функция для безопасной загрузки секретов ---
def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """
    Получает значение секрета из Google Cloud Secret Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GCP_PROJECT_ID}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# --- Настройки Базы Данных (для Cloud SQL) ---
DB_USER = config("DB_USER")
DB_NAME = config("DB_NAME")
DB_INSTANCE_NAME = config("DB_INSTANCE_NAME")
DB_PASSWORD = get_secret("DB_PASSWORD")

# Строка подключения, использующая Cloud SQL Auth Proxy
DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
    f"?host=/cloudsql/{GCP_PROJECT_ID}:{GCP_REGION}:{DB_INSTANCE_NAME}"
)

# --- Настройки Redis (для Memorystore) ---
REDIS_URL = config("REDIS_URL") # Получаем готовую строку подключения

# --- Настройки Vertex AI ---
VERTEX_AI_ENDPOINT_ID = config("VERTEX_AI_ENDPOINT_ID")

# --- Ключи API и другие секреты ---
SECRET_KEY = get_secret("SECRET_KEY")
GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
