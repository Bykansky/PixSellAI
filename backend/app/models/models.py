from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_path = Column(String, nullable=True)

    swipes = relationship("Swipe", back_populates="product")
    generations = relationship("Generation", back_populates="product")

class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    direction = Column(String, nullable=False)  # left / right
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="swipes")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    style = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending / completed / failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="generations")
