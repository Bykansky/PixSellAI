import uuid
import json
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from .. import schemas, tasks, db, config
from google.cloud import storage

router = APIRouter()

def get_db_session():
    db_session = db.SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()

@router.post("/generate", response_model=schemas.GenerationJobResponse)
def create_generation_job(
    sku: str = Form(None),
    product_data_json: str = Form(...), # Принимаем данные о продукте как строку JSON
    file: UploadFile = File(...),
    db_session: Session = Depends(get_db_session)
):
    """
    Принимает фото товара, текстовые данные, сохраняет всё
    и ставит задачу на генерацию в очередь.
    """
    # Преобразуем строку JSON в словарь Python
    product_data = json.loads(product_data_json)

    # 1. Загружаем исходный файл в Google Cloud Storage
    gcs_client = storage.Client()
    bucket = gcs_client.bucket(config.BUCKET_NAME)
    
    file_extension = file.filename.split('.')[-1]
    blob_name = f"originals/{uuid.uuid4()}.{file_extension}"
    blob = bucket.blob(blob_name)
    
    blob.upload_from_file(file.file, content_type=file.content_type)

    # 2. Создаем запись о продукте в нашей БД, сохраняя текстовые данные в поле JSON
    new_product = db.Product(
        sku=sku,
        original_image_gcs_path=blob_name,
        product_info=product_data # Сохраняем весь словарь
    )
    db_session.add(new_product)
    db_session.commit()
    db_session.refresh(new_product)

    # 3. Ставим задачу в очередь Redis, передавая всю необходимую информацию
    job = tasks.enqueue_generation(
        product_id=str(new_product.id),
        gcs_path=blob_name,
        style="photorealistic",
        product_data=product_data # Передаем данные в воркер
    )

    return {"job_id": job.get_id(), "product_id": new_product.id}
