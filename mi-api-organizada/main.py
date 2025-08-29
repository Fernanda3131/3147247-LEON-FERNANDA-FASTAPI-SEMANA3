from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Routers
from routers.products import router as products_router
from routers import book, borrowing, categories, health

# Excepciones personalizadas
from exceptions.custom_exceptions import (
    BookNotFoundError, DuplicateISBNError, InvalidBookDataError,
    BookNotAvailableError, LibraryFullError
)

# Utils
from utils.exception_handlers import register_exception_handlers

# Configuración de logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Mi API Organizada y Biblioteca API",
    description="API de productos y libros con estructura profesional",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Handlers globales de errores
@app.exception_handler(BookNotFoundError)
async def book_not_found_handler(request: Request, exc: BookNotFoundError):
    logger.warning(exc.message)
    return JSONResponse(status_code=404, content={"error": exc.message})

@app.exception_handler(DuplicateISBNError)
async def duplicate_isbn_handler(request: Request, exc: DuplicateISBNError):
    logger.error(exc.message)
    return JSONResponse(status_code=400, content={"error": exc.message})

@app.exception_handler(InvalidBookDataError)
async def invalid_data_handler(request: Request, exc: InvalidBookDataError):
    logger.error(exc.message)
    return JSONResponse(status_code=422, content={"error": exc.message})

@app.exception_handler(BookNotAvailableError)
async def not_available_handler(request: Request, exc: BookNotAvailableError):
    logger.warning(exc.message)
    return JSONResponse(status_code=400, content={"error": exc.message})

@app.exception_handler(LibraryFullError)
async def library_full_handler(request: Request, exc: LibraryFullError):
    logger.warning(exc.message)
    return JSONResponse(status_code=400, content={"error": exc.message})

# Registrar manejadores globales automáticos
register_exception_handlers(app)

# Incluir routers
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(book.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(borrowing.router, prefix="/api/v1/borrowing", tags=["Borrowing"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(health.router)

# Health check
@app.get("/health")
def health_check():
    return {"success": True, "message": "API running", "timestamp": "2025-08-28"}

# Punto de entrada
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)