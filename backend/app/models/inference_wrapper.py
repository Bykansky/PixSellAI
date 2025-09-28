# backend/app/models/inference_wrapper.py
import os
import io
import base64
import uuid
import requests
from pathlib import Path
from PIL import Image
from typing import List, Dict, Any

# Load env
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[3] / ".env")

HF_API_KEY = os.getenv("HF_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

RESULTS_DIR = os.getenv("RESULTS_DIR", "backend/results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ------------------------------
# Helper: save image bytes -> file
# ------------------------------
def _save_bytes(b: bytes, out_dir: str, tag: str) -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{uuid.uuid4().hex}_{tag}.png"
    path = Path(out_dir) / fname
    with open(path, "wb") as f:
        f.write(b)
    return str(path)

def _save_pil(img: Image.Image, out_dir: str, tag: str) -> str:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    fname = f"{uuid.uuid4().hex}_{tag}.png"
    path = Path(out_dir) / fname
    img.save(path, format="PNG", compress_level=1)
    return str(path)

# ------------------------------
# Provider: Hugging Face Inference API (HTTP)
# ------------------------------
def generate_hf(prompt: str, out_dir: str, idx: int = 0, model: str = "stabilityai/stable-diffusion-xl-base-1-0") -> Dict[str, Any]:
    """
    Uses Hugging Face Inference API (simple POST).
    model: HF model id, e.g. "stabilityai/stable-diffusion-xl-base-1-0"
    Returns dict with 'path' to saved image and metadata.
    """
    if not HF_API_KEY:
        return {"error": "HF_API_KEY not set"}

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}
    # If model expects params, add them in payload['parameters'] e.g. {"width":1024, "height":1024}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
    except Exception as e:
        return {"error": f"HF request failed: {e}"}

    # Response can be raw bytes (image) or JSON with base64. Handle both.
    content_type = resp.headers.get("content-type", "")
    if content_type.startswith("image/"):
        path = _save_bytes(resp.content, out_dir, f"hf_{idx}")
        return {"model": "huggingface", "path": path, "prompt": prompt}
    else:
        # Attempt to decode JSON that contains base64 image(s)
        try:
            data = resp.json()
            # common shapes: {'images': ['data:...base64,...']} or {'generated_image': 'base64...'} or list
            # Try multiple heuristics:
            if isinstance(data, dict):
                # scan values for base64
                for v in data.values():
                    if isinstance(v, str) and v.strip().startswith("data:image"):
                        b64 = v.split(",", 1)[1]
                        img_bytes = base64.b64decode(b64)
                        path = _save_bytes(img_bytes, out_dir, f"hf_{idx}")
                        return {"model": "huggingface", "path": path, "prompt": prompt}
                if "generated_image" in data and isinstance(data["generated_image"], str):
                    b64 = data["generated_image"]
                    if b64.startswith("data:"):
                        b64 = b64.split(",", 1)[1]
                    img_bytes = base64.b64decode(b64)
                    path = _save_bytes(img_bytes, out_dir, f"hf_{idx}")
                    return {"model": "huggingface", "path": path, "prompt": prompt}
                if "images" in data and isinstance(data["images"], list) and data["images"]:
                    item = data["images"][0]
                    if isinstance(item, str) and item.startswith("data:"):
                        b64 = item.split(",", 1)[1]
                        img_bytes = base64.b64decode(b64)
                        path = _save_bytes(img_bytes, out_dir, f"hf_{idx}")
                        return {"model": "huggingface", "path": path, "prompt": prompt}
            # fallback: sometimes HF returns bytes-as-json in list
            if isinstance(data, list) and data:
                first = data[0]
                if isinstance(first, dict) and "generated_image" in first:
                    b64 = first["generated_image"]
                    img_bytes = base64.b64decode(b64)
                    path = _save_bytes(img_bytes, out_dir, f"hf_{idx}")
                    return {"model": "huggingface", "path": path, "prompt": prompt}
        except Exception:
            pass
    return {"error": "HF: could not parse response", "status_code": resp.status_code, "text": resp.text[:400]}

# ------------------------------
# Provider: Google GenAI (Gemini / Imagen) via google-genai SDK
# ------------------------------
def generate_gemini(prompt: str, out_dir: str, idx: int = 0, model: str = "gemini-2.5-flash-image-preview") -> Dict[str, Any]:
    """
    Uses google-genai Python SDK. Requires GOOGLE_API_KEY in env or provided earlier.
    Returns saved file path.
    """
    if not GOOGLE_API_KEY:
        return {"error": "GOOGLE_API_KEY not set"}
    try:
        from google import genai
        from google.genai import types
    except Exception as e:
        return {"error": f"google-genai lib not installed: {e}"}

    # create client (Gemini Developer API using API key)
    client = genai.Client(api_key=GOOGLE_API_KEY)
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=[types.Modality.IMAGE],
                candidate_count=1
            )
        )
    except Exception as e:
        return {"error": f"Gemini request failed: {e}"}

    # Response: iterate parts for image bytes (inline_data)
    try:
        # response.candidates may exist
        if hasattr(response, "candidates") and response.candidates:
            cand = response.candidates[0]
            # cand.content.parts may contain inline_data
            for part in getattr(cand, "content").parts:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    # inline.data could be bytes-like
                    raw = inline.data
                    # Sometimes it's already bytes, sometimes base64
                    if isinstance(raw, str):
                        # try base64
                        raw = base64.b64decode(raw)
                    path = _save_bytes(raw, out_dir, f"gemini_{idx}")
                    return {"model": "gemini", "path": path, "prompt": prompt}
        # fallback: check response.text or other fields
        if hasattr(response, "text") and response.text:
            return {"model": "gemini", "text": response.text}
    except Exception as e:
        return {"error": f"Gemini parse failed: {e}"}

    return {"error": "Gemini: no image returned in response"}

# ------------------------------
# High-level: ensemble generator
# ------------------------------
def generate_ensemble(file_bytes: bytes, style: str, out_dir: str, n_variants: int = 2) -> List[Dict[str, Any]]:
    """
    file_bytes: original uploaded image bytes (may be used for image2image later)
    style: e.g. "minimal", "luxury", "white background"
    out_dir: folder to save results
    Returns list of dicts: [{'model':..., 'path':..., 'prompt':...}, ...]
    """
    prompt = f"Product photo, {style}. High-quality, studio lighting, white background, photorealistic"
    results = []

    # 1) call HF
    for i in range(1):
        r = generate_hf(prompt, out_dir, idx=i)
        results.append(r)

    # 2) call Gemini (Google)
    for i in range(1):
        r = generate_gemini(prompt, out_dir, idx=i)
        results.append(r)

    # Filter out errors
    results = [x for x in results if x and not x.get("error")]
    return results
