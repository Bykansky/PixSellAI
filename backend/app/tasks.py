# backend/app/tasks.py
import os
import uuid
from redis import Redis
from rq import Queue
from pathlib import Path
from app.db import SessionLocal
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_conn = Redis.from_url(REDIS_URL)
q = Queue("default", connection=redis_conn, default_timeout=3600)

def enqueue_generation(product_id: str, input_bytes: bytes, style: str):
    """
    Queue a generation job. Returns job id.
    input_bytes: raw bytes of uploaded file
    """
    job = q.enqueue(_do_generate, product_id, input_bytes, style)
    return job.get_id()

def _do_generate(product_id: str, input_bytes: bytes, style: str):
    # heavy ML imports here
    from app.models.inference_wrapper import generate_ensemble
    out_dir = Path("backend/results") / product_id
    out_dir.mkdir(parents=True, exist_ok=True)

    # run ensemble
    results = generate_ensemble(input_bytes, style, str(out_dir), n_variants=2)

    # save metadata to DB
    db = SessionLocal()
    try:
        for r in results:
            # simple DB insert: ensure table 'generations' exists in app.db
            from app.db import Generation
            gen = Generation(
                product_id=product_id,
                style=style,
                result_url=str(r.get("path"))
            )
            db.add(gen)
        db.commit()
    finally:
        db.close()
    return {"status": "done", "files": [r.get("path") for r in results]}
