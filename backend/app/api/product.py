from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal, Product

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
