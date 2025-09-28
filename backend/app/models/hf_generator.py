import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("❌ Hugging Face API token не найден в .env")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2"

HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}


def generate_image(prompt: str, output_path: str = "uploads/generated.png") -> str:
    """
    Отправляет запрос к Hugging Face и сохраняет картинку.
    """
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ошибка генерации: {response.text}")

    with open(output_path, "wb") as f:
        f.write(response.content)

    return output_path
