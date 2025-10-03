import uuid
import datetime
from sqlalchemy import create_engine, Column, DateTime, String, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from . import config

engine = create_engine(
    config.DATABASE_URL,
    connect_args={"options": "-c timezone=utc"}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String, index=True, nullable=True)
    original_image_gcs_path = Column(String, nullable=False)
    product_info = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    generations = relationship("Generation", back_populates="product", cascade="all, delete-orphan")

class Generation(Base):
    __tablename__ = "generations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    generated_image_gcs_path = Column(String, nullable=False)
    model_used = Column(String)
    prompt = Column(String, nullable=True)
    is_liked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    product = relationship("Product", back_populates="generations")

def init_db():
    Base.metadata.create_all(bind=engine)
