from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import List
from datetime import date

class Book(BaseModel):
    title: str
    author: str
    rating: float = Field(..., ge=0, le=5)
    bestseller: bool = False
    tags: List[str] = []
    year: int
    price: float

    # 1. Validar título capitalizado
    @model_validator(mode="after")
    def check_title(cls, values):
        values.title = values.title.title()
        return values

    # 2. Validar que el autor no sea solo números
    @model_validator(mode="after")
    def check_author(cls, values):
        if values.author.isdigit():
            raise ValueError("El autor no puede ser solo números")
        return values

    # 3. Si es bestseller debe tener rating >= 4.0
    @model_validator(mode="after")
    def check_bestseller(cls, values):
        if values.bestseller and values.rating < 4.0:
            raise ValueError("Un bestseller debe tener rating >= 4.0")
        return values

    # 4. Los tags no deben estar duplicados
    @model_validator(mode="after")
    def check_tags(cls, values):
        if len(values.tags) != len(set(values.tags)):
            raise ValueError("Los tags no pueden estar duplicados")
        return values

    # 5. Libros muy antiguos (< 1900) deben tener precio especial
    @model_validator(mode="after")
    def check_year(cls, values):
        if values.year < 1900 and values.price >= 50:
            raise ValueError("Los libros antiguos (<1900) deben tener precio especial (<50)")
        return values