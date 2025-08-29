from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from models.product import ProductCreate, ProductUpdate, ProductResponse
from services.product_service import ProductService
from fastapi import HTTPException, status


router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=List[ProductResponse])
def get_products():
    return ProductService.get_all_products()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    
    product = ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return product

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate):
    try:
        return ProductService.create_product(product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    updated = ProductService.update_product(product_id, product)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return updated

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    deleted = ProductService.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return None

@router.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id not in ProductService:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    return ProductService[product_id]

@router.get("/products/search")
def search_products(
    name: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
) -> List[dict]:
    """Buscar productos por nombre y rango de precio"""
    try:
        # Obtener todos los productos
        results = ProductService.copy()

        # Filtrar por nombre si se proporciona
        if name:
            name_lower = name.lower().strip()
            if len(name_lower) < 2:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El término de búsqueda debe tener al menos 2 caracteres"
                )
            results = [p for p in results if name_lower in p["name"].lower()]

        # Filtrar por precio mínimo
        if min_price is not None:
            if min_price < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio mínimo no puede ser negativo"
                )
            results = [p for p in results if p["price"] >= min_price]

        # Filtrar por precio máximo
        if max_price is not None:
            if max_price < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio máximo no puede ser negativo"
                )
            results = [p for p in results if p["price"] <= max_price]

        # Validar rango de precios
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio mínimo no puede ser mayor al máximo"
                )

        return results

    except HTTPException:
        raise
    except Exception as e:
        # Log del error (opcional)
        print(f"Error en búsqueda: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )