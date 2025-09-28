from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, Swipe

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/swipe/{product_id}")
def swipe_product(product_id: int, direction: str, db: Session = Depends(get_db)):
    swipe = Swipe(product_id=product_id, direction=direction)
    db.add(swipe)
    db.commit()
    db.refresh(swipe)
    return swipe
