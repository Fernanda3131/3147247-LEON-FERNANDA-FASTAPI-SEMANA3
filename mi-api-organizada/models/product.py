from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, validator

class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0, le=1000000)
    stock: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if v.strip() != v:
            raise ValueError('El nombre no puede empezar o terminar con espacios')
        return v.title()

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    price: Optional[float] = Field(None, gt=0, le=1000000)
    stock: Optional[int] = Field(None, ge=0)

class ProductResponse(ProductBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Product(BaseModel):
    name: str
    price: float

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.title()