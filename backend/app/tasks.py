import io
import uuid
import base64
import sys
from redis import Redis
from rq import Queue
from . import config, db
from google.cloud import storage, aiplatform
from PIL import Image
from rembg import remove
import google.generativeai as genai

# --- Настройки Redis ---
redis_conn = Redis.from_url(config.REDIS_URL)
q = Queue("default", connection=redis_conn, default_timeout=1800)

# --- Вспомогательные AI-функции ---
def _get_image_description_with_gemini(image: Image.Image) -> str:
    """Отправляет изображение в Gemini Pro Vision и возвращает его описание."""
    print("Connecting to Gemini Vision API...")
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro-vision')
    prompt = "You are an expert marketer. Analyze this product image and provide a concise, factual description. Describe the main object, its material, color, and key visual features."
    response = model.generate_content([prompt, image])
    print("Gemini Vision Analysis successful.")
    return response.text

# --- Основные функции для очереди задач ---
def enqueue_generation(product_id: str, gcs_path: str, style: str, product_data: dict):
    """Ставит задачу генерации в очередь."""
    job = q.enqueue(_do_generate_background, product_id, gcs_path, style, product_data)
    return job

def _do_generate_background(product_id: str, gcs_path: str, style: str, product_data: dict):
    """Эта функция выполняется в фоновом режиме воркером RQ."""
    print(f"Received job for product {product_id} with data: {product_data}")

    db_session = db.SessionLocal()
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(config.BUCKET_NAME)

    try:
        # Шаг 1: Скачать изображение
        blob = bucket.blob(gcs_path)
        in_mem_file = io.BytesIO()
        blob.download_to_file(in_mem_file)
        in_mem_file.seek(0)
        original_image = Image.open(in_mem_file).convert("RGB")
        
        # Шаг 2: Проанализировать изображение с помощью Gemini Vision
        visual_description = _get_image_description_with_gemini(original_image)
        
        # Шаг 3: Удалить фон
        product_no_bg = remove(original_image)

        # Шаг 4: Сгенерировать новый фон через Vertex AI
        prompt = f"professional product photography of an item, on a clean white marble countertop, {style}, high detail, 8k, soft lighting, inspired by: {visual_description}"
        
        aiplatform.init(project=config.GCP_PROJECT_ID, location=config.GCP_REGION)
        endpoint = aiplatform.Endpoint(endpoint_name=config.VERTEX_AI_ENDPOINT_ID)
        response = endpoint.predict(instances=[{"prompt": prompt}])
        generated_bg_bytes = base64.b64decode(response.predictions[0]['bytesBase64Encoded'])
        generated_bg_image = Image.open(io.BytesIO(generated_bg_bytes))
        
        # Шаг 5: Собрать финальное изображение
        generated_bg_image = generated_bg_image.resize(original_image.size)
        generated_bg_image.paste(product_no_bg, (0, 0), product_no_bg)
        final_image = generated_bg_image

        # Шаг 6: Загрузить результат в GCS
        out_mem_file = io.BytesIO()
        final_image.save(out_mem_file, format="PNG")
        out_mem_file.seek(0)
        generated_blob_name = f"generated/{uuid.uuid4()}.png"
        generated_blob = bucket.blob(generated_blob_name)
        generated_blob.upload_from_file(out_mem_file, content_type="image/png")

        # Шаг 7: Сохранить метаданные в БД
        new_generation = db.Generation(
            product_id=uuid.UUID(product_id),
            generated_image_gcs_path=generated_blob_name,
            model_used="VertexAI-SD-XL_&_Gemini-Vision",
            prompt=prompt
        )
        db_session.add(new_generation)
        db_session.commit()
        
        return {"status": "success", "gcs_path": generated_blob_name}
    except Exception as e:
        print(f"Error in job for product {product_id}: {e}", file=sys.stderr)
        return {"status": "error", "message": str(e)}
    finally:
        db_session.close()
