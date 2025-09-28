from fastapi import APIRouter, UploadFile, Form
from app.models.hf_generator import generate_image
import os

router = APIRouter()


@router.post("/api/generate")
async def generate(product_id: int = Form(...), style: str = Form("default")):
    """
    Генерация изображения через Hugging Face
    """
    prompt = f"Product {product_id} styled as {style}"

    output_path = f"uploads/generated_{product_id}.png"
    result_path = generate_image(prompt, output_path)

    return {"image_url": result_path}
