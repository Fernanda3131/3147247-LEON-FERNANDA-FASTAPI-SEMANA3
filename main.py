from fastapi import FastAPI, HTTPException, Query, Path, status, Response, Depends
from fastapi.responses import JSONResponse
from typing import Optional, List
from pydantic import BaseModel, validator, Field, EmailStr, model_validator
import re
from datetime import datetime
import logging

# Aquí asumo que importas estos modelos y funciones de tus módulos
from models.product_models import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductList, CategoryEnum, ErrorResponse
)
from data.products_data import (
    get_all_products, get_product_by_id, create_product,
    update_product, delete_product, filter_products
)

app = FastAPI(
    title="API de Inventario - Semana 3",
    description="API REST completa para manejo de productos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# -----------------------------
# ENDPOINT BÁSICO
# -----------------------------
@app.get("/", summary="Endpoint de bienvenida")
async def root():
    return {
        "message": "API de Inventario - Semana 3",
        "version": "1.0.0",
        "docs": "/docs"
    }

# -----------------------------
# CRUD DE PRODUCTOS
# -----------------------------
@app.get("/products", response_model=ProductList)
async def get_products(
    category: Optional[CategoryEnum] = Query(None),
    in_stock: Optional[bool] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None, min_length=1)
):
    try:
        products = filter_products(
            category=category.value if category else None,
            in_stock=in_stock,
            min_price=min_price,
            max_price=max_price
        )

        if search:
            search_lower = search.lower()
            products = [
                p for p in products
                if search_lower in p["name"].lower() or
                (p.get("description") and search_lower in p["description"].lower())
            ]

        total = len(products)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_products = products[start_index:end_index]

        return ProductList(
            products=paginated_products,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int = Path(..., gt=0)):
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado")
    return ProductResponse(**product)


@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_new_product(product: ProductCreate):
    try:
        existing_products = get_all_products()
        for existing in existing_products:
            if existing["name"].lower() == product.name.lower():
                raise HTTPException(
                    status_code=409,
                    detail=f"Ya existe un producto con el nombre '{product.name}'"
                )

        product_data = product.dict()
        new_product = create_product(product_data)
        return ProductResponse(**new_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear producto: {str(e)}")


@app.put("/products/{product_id}", response_model=ProductResponse)
async def update_existing_product(
    product: ProductUpdate,
    product_id: int = Path(..., gt=0)
):
    try:
        existing_product = get_product_by_id(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado")

        all_products = get_all_products()
        for existing in all_products:
            if existing["id"] != product_id and existing["name"].lower() == product.name.lower():
                raise HTTPException(status_code=409, detail=f"Ya existe otro producto con el nombre '{product.name}'")

        product_data = product.dict()
        updated_product = update_product(product_id, product_data)
        return ProductResponse(**updated_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar producto: {str(e)}")


@app.delete("/products/{product_id}", status_code=204)
async def delete_existing_product(product_id: int = Path(..., gt=0)):
    existing_product = get_product_by_id(product_id)
    if not existing_product:
        raise HTTPException(status_code=404, detail=f"Producto con ID {product_id} no encontrado")

    deleted = delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Error al eliminar el producto")

    return Response(status_code=204)


# -----------------------------
# MODELOS EXTRA (USER, PRODUCT, ORDER, REGISTRATION)
# -----------------------------
class User(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    age: int = Field(..., ge=18, le=100)
    phone: str = Field(..., min_length=10, max_length=15)

    @validator('phone')
    def validate_phone(cls, v):
        phone_clean = re.sub(r'[\s\-]', '', v)
        if not phone_clean.isdigit():
            raise ValueError('Teléfono debe contener solo números')
        return phone_clean


class Product(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    price: float = Field(..., gt=0, le=1000000)
    category: str = Field(..., pattern=r'^[a-zA-Z\s]+$')
    stock: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if v.strip() != v:
            raise ValueError('El nombre no puede empezar o terminar con espacios')
        return v.title()


class Order(BaseModel):
    product_name: str = Field(..., min_length=3)
    quantity: int = Field(..., gt=0, le=100)
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    discount_percent: float = Field(0, ge=0, le=50)
    shipping_required: bool = True
    shipping_cost: float = Field(0, ge=0)

    @model_validator(mode="after")
    def validate_all(cls, model):
        subtotal = model.quantity * model.unit_price
        discount_amount = subtotal * (model.discount_percent / 100)
        expected_total = subtotal - discount_amount

        if abs(model.total_price - expected_total) > 0.01:
            raise ValueError(f'Total incorrecto. Esperado: {expected_total:.2f}, Recibido: {model.total_price:.2f}')

        if model.shipping_required and model.shipping_cost == 0:
            raise ValueError('Si requiere envío, el costo debe ser mayor a 0')

        if not model.shipping_required and model.shipping_cost > 0:
            raise ValueError('Si no requiere envío, el costo debe ser 0')

        return model


class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    age: int = Field(..., ge=13, le=120)
    terms_accepted: bool

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username solo puede contener letras, números y _')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe tener al menos una mayúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password debe tener al menos un número')
        return v

    @model_validator(mode="after")
    def validate_passwords_and_terms(cls, model):
        if model.password != model.confirm_password:
            raise ValueError('Las contraseñas no coinciden')
        if not model.terms_accepted:
            raise ValueError('Debe aceptar los términos y condiciones')
        if model.age < 18 and model.terms_accepted:
            raise ValueError('Menores de 18 necesitan autorización parental')
        return model


# -----------------------------
# ENDPOINTS EXTRA
# -----------------------------
@app.post("/orders/validate")
def create_order(order: Order):
    return {
        "message": "Orden válida",
        "order": order.dict(),
        "calculated_total": order.quantity * order.unit_price * (1 - order.discount_percent / 100)
    }


@app.post("/users/register")
def register_user(user: UserRegistration):
    return {
        "message": f"Usuario {user.username} registrado con éxito",
        "user": user.dict(exclude={"password", "confirm_password"})
    }


# -----------------------------
# NUEVOS FILTROS (ProductFilters)
# -----------------------------
class ProductFilters:
    def __init__(
        self,
        name: Optional[str] = Query(None, min_length=2, max_length=50),
        min_price: Optional[float] = Query(None, ge=0, le=1000000),
        max_price: Optional[float] = Query(None, ge=0, le=1000000),
        category: Optional[str] = Query(None, regex=r'^[a-zA-Z\s]+$'),
        in_stock: Optional[bool] = Query(None),
        tags: Optional[List[str]] = Query(None),
        page: int = Query(1, ge=1, le=100),
        limit: int = Query(10, ge=1, le=50)
    ):
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValueError("min_price no puede ser mayor que max_price")

        self.name = name
        self.min_price = min_price
        self.max_price = max_price
        self.category = category
        self.in_stock = in_stock
        self.tags = tags
        self.page = page
        self.limit = limit


@app.get("/products/search")
def search_products(filters: ProductFilters = Depends()):
    all_products = [
        {"id": 1, "name": "Laptop Gaming", "price": 1500.0, "category": "electronics", "in_stock": True, "tags": ["gaming", "powerful"]},
        {"id": 2, "name": "Mouse Wireless", "price": 50.0, "category": "electronics", "in_stock": True, "tags": ["wireless", "ergonomic"]},
        {"id": 3, "name": "Teclado Mecánico", "price": 120.0, "category": "electronics", "in_stock": False, "tags": ["mechanical", "rgb"]},
        {"id": 4, "name": "Monitor 4K", "price": 800.0, "category": "electronics", "in_stock": True, "tags": ["4k", "gaming"]},
        {"id": 5, "name": "Camiseta Deportiva", "price": 25.0, "category": "clothing", "in_stock": True, "tags": ["sport", "comfortable"]}
    ]

    filtered_products = all_products.copy()

    if filters.name:
        filtered_products = [p for p in filtered_products if filters.name.lower() in p["name"].lower()]

    if filters.min_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] >= filters.min_price]

    if filters.max_price is not None:
        filtered_products = [p for p in filtered_products if p["price"] <= filters.max_price]

    if filters.category:
        filtered_products = [p for p in filtered_products if p["category"] == filters.category]

    if filters.in_stock is not None:
        filtered_products = [p for p in filtered_products if p["in_stock"] == filters.in_stock]

    if filters.tags:
        filtered_products = [p for p in filtered_products if any(tag in p["tags"] for tag in filters.tags)]

    start = (filters.page - 1) * filters.limit
    end = start + filters.limit
    paginated_products = filtered_products[start:end]

    return {
        "products": paginated_products,
        "total": len(filtered_products),
        "page": filters.page,
        "limit": filters.limit,
        "total_pages": (len(filtered_products) + filters.limit - 1) // filters.limit,
        "filters_applied": {
            "name": filters.name,
            "price_range": f"{filters.min_price}-{filters.max_price}",
            "category": filters.category,
            "in_stock": filters.in_stock,
            "tags": filters.tags
        }
    }


@app.get("/products/price-range")
def get_products_by_price(
    min_price: float = Query(..., ge=0, le=1000000),
    max_price: float = Query(..., ge=0, le=1000000)
):
    if min_price > max_price:
        raise HTTPException(status_code=400, detail="El precio mínimo no puede ser mayor al precio máximo")

    return {
        "message": f"Buscando productos entre ${min_price} y ${max_price}",
        "range": {"min": min_price, "max": max_price},
        "range_valid": True
    }

# Agregar a tu main.py existente de Semana 2


# Lista simple para simular base de datos
products = [
    {"id": 1, "name": "Laptop", "price": 1500.0, "stock": 10},
    {"id": 2, "name": "Mouse", "price": 25.0, "stock": 50},
    {"id": 3, "name": "Teclado", "price": 75.0, "stock": 0}
]

# Endpoint con manejo de errores básico
@app.get("/products/{product_id}")
def get_product(product_id: int):
    # Error: ID inválido
    if product_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID del producto debe ser mayor a 0"
        )

    # Buscar producto
    for product in products:
        if product["id"] == product_id:
            return {"success": True, "product": product}

    # Error: No encontrado
    raise HTTPException(
        status_code=404,
        detail=f"Producto con ID {product_id} no encontrado"
    )

@app.post("/products")
def create_product(product: dict):
    # Validación básica
    if "name" not in product:
        raise HTTPException(
            status_code=400,
            detail="El campo 'name' es obligatorio"
        )

    if "price" not in product:
        raise HTTPException(
            status_code=400,
            detail="El campo 'price' es obligatorio"
        )

    if product["price"] <= 0:
        raise HTTPException(
            status_code=400,
            detail="El precio debe ser mayor a 0"
        )

    # Verificar que no exista el nombre
    for existing in products:
        if existing["name"].lower() == product["name"].lower():
            raise HTTPException(
                status_code=409,
                detail=f"Ya existe un producto con el nombre '{product['name']}'"
            )

    # Crear producto
    new_id = max([p["id"] for p in products]) + 1
    new_product = {
        "id": new_id,
        "name": product["name"],
        "price": product["price"],
        "stock": product.get("stock", 0)
    }

    products.append(new_product)
    return {"success": True, "product": new_product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    # Buscar y eliminar
    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(i)
            return {"success": True, "message": f"Producto '{deleted_product['name']}' eliminado"}

    # Error: No encontrado
    raise HTTPException(
        status_code=404,
        detail=f"No se puede eliminar: producto con ID {product_id} no existe"
    )


# Función para crear respuestas de error consistentes
def create_error_response(message: str, status_code: int, details: dict = None):
    return {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
    }

# Función para crear respuestas de éxito consistentes
def create_success_response(message: str, data: dict = None):
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    }

# Actualizar endpoints con respuestas consistentes
@app.get("/products/{product_id}")
def get_product(product_id: int):
    if product_id <= 0:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="ID del producto debe ser mayor a 0",
                status_code=400,
                details={"provided_id": product_id, "min_id": 1}
            )
        )

    for product in products:
        if product["id"] == product_id:
            return create_success_response(
                message="Producto encontrado",
                data={"product": product}
            )

    raise HTTPException(
        status_code=404,
        detail=create_error_response(
            message=f"Producto con ID {product_id} no encontrado",
            status_code=404,
            details={"requested_id": product_id, "available_ids": [p["id"] for p in products]}
        )
    )

@app.post("/products")
def create_product(product: dict):
    # Validaciones con respuestas consistentes
    if "name" not in product:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'name' es obligatorio",
                status_code=400,
                details={"missing_field": "name", "received_fields": list(product.keys())}
            )
        )

    if "price" not in product:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'price' es obligatorio",
                status_code=400,
                details={"missing_field": "price", "received_fields": list(product.keys())}
            )
        )

    if product["price"] <= 0:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El precio debe ser mayor a 0",
                status_code=400,
                details={"provided_price": product["price"], "min_price": 0.01}
            )
        )

    # Verificar duplicados
    for existing in products:
        if existing["name"].lower() == product["name"].lower():
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    message=f"Ya existe un producto con el nombre '{product['name']}'",
                    status_code=409,
                    details={
                        "conflicting_name": product["name"],
                        "existing_product_id": existing["id"]
                    }
                )
            )

    # Crear producto
    new_id = max([p["id"] for p in products]) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": product["name"],
        "price": product["price"],
        "stock": product.get("stock", 0)
    }

    products.append(new_product)
    return create_success_response(
        message=f"Producto '{new_product['name']}' creado exitosamente",
        data={"product": new_product}
    )

# Endpoint para listar todos los productos
@app.get("/products")
def get_all_products():
    return create_success_response(
        message=f"Se encontraron {len(products)} productos",
        data={
            "products": products,
            "total": len(products)
        }
    )


# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Actualizar endpoints con logging
@app.get("/products/{product_id}")
def get_product(product_id: int):
    logger.info(f"Buscando producto con ID: {product_id}")

    if product_id <= 0:
        logger.warning(f"ID inválido recibido: {product_id}")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="ID del producto debe ser mayor a 0",
                status_code=400,
                details={"provided_id": product_id, "min_id": 1}
            )
        )

    for product in products:
        if product["id"] == product_id:
            logger.info(f"Producto encontrado: {product['name']}")
            return create_success_response(
                message="Producto encontrado",
                data={"product": product}
            )

    logger.warning(f"Producto no encontrado: ID {product_id}")
    raise HTTPException(
        status_code=404,
        detail=create_error_response(
            message=f"Producto con ID {product_id} no encontrado",
            status_code=404,
            details={"requested_id": product_id, "available_ids": [p["id"] for p in products]}
        )
    )

@app.post("/products")
def create_product(product: dict):
    logger.info(f"Intentando crear producto: {product.get('name', 'SIN_NOMBRE')}")

    # Validaciones con logging
    if "name" not in product:
        logger.error("Intento de crear producto sin nombre")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'name' es obligatorio",
                status_code=400,
                details={"missing_field": "name", "received_fields": list(product.keys())}
            )
        )

    if "price" not in product:
        logger.error(f"Intento de crear producto '{product['name']}' sin precio")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'price' es obligatorio",
                status_code=400,
                details={"missing_field": "price", "received_fields": list(product.keys())}
            )
        )

    if product["price"] <= 0:
        logger.error(f"Precio inválido para producto '{product['name']}': {product['price']}")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El precio debe ser mayor a 0",
                status_code=400,
                details={"provided_price": product["price"], "min_price": 0.01}
            )
        )

    # Verificar duplicados
    for existing in products:
        if existing["name"].lower() == product["name"].lower():
            logger.warning(f"Intento de crear producto duplicado: '{product['name']}'")
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    message=f"Ya existe un producto con el nombre '{product['name']}'",
                    status_code=409,
                    details={
                        "conflicting_name": product["name"],
                        "existing_product_id": existing["id"]
                    }
                )
            )

    # Crear producto
    new_id = max([p["id"] for p in products]) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": product["name"],
        "price": product["price"],
        "stock": product.get("stock", 0)
    }

    products.append(new_product)
    logger.info(f"Producto creado exitosamente: ID {new_id}, Nombre: {new_product['name']}")

    return create_success_response(
        message=f"Producto '{new_product['name']}' creado exitosamente",
        data={"product": new_product}
    )

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    logger.info(f"Intentando eliminar producto con ID: {product_id}")

    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(i)
            logger.info(f"Producto eliminado: ID {product_id}, Nombre: {deleted_product['name']}")
            return create_success_response(
                message=f"Producto '{deleted_product['name']}' eliminado exitosamente",
                data={"deleted_product": deleted_product}
            )

    logger.warning(f"Intento de eliminar producto inexistente: ID {product_id}")
    raise HTTPException(
        status_code=404,
        detail=create_error_response(
            message=f"No se puede eliminar: producto con ID {product_id} no existe",
            status_code=404,
            details={"requested_id": product_id, "available_ids": [p["id"] for p in products]}
        )
    )

# Endpoint para estadísticas (con logging)
@app.get("/stats")
def get_stats():
    logger.info("Consultando estadísticas de la API")

    total_products = len(products)
    total_stock = sum(p.get("stock", 0) for p in products)
    avg_price = sum(p["price"] for p in products) / total_products if total_products > 0 else 0

    stats = {
        "total_products": total_products,
        "total_stock": total_stock,
        "average_price": round(avg_price, 2)
    }

    logger.info(f"Estadísticas calculadas: {stats}")

    return create_success_response(
        message="Estadísticas calculadas exitosamente",
        data={"stats": stats}
    )