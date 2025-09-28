from fastapi import APIRouter

router = APIRouter()

@router.post("/train")
def train_model():
    return {"status": "training started"}
