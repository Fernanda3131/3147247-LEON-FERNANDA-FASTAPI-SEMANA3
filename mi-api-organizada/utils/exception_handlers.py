from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from exceptions.custom_exceptions import (
    BookNotFoundError, DuplicateISBNError,
    InvalidBookDataError, BookNotAvailableError,
    LibraryFullError
)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(BookNotFoundError)
    async def book_not_found_handler(request: Request, exc: BookNotFoundError):
        return JSONResponse(
            status_code=404,
            content={"error": f"Libro no encontrado: {exc}"}
        )

    @app.exception_handler(DuplicateISBNError)
    async def duplicate_isbn_handler(request: Request, exc: DuplicateISBNError):
        return JSONResponse(
            status_code=400,
            content={"error": f"ISBN duplicado: {exc}"}
        )

    @app.exception_handler(InvalidBookDataError)
    async def invalid_data_handler(request: Request, exc: InvalidBookDataError):
        return JSONResponse(
            status_code=422,
            content={"error": str(exc)}
        )

    @app.exception_handler(BookNotAvailableError)
    async def not_available_handler(request: Request, exc: BookNotAvailableError):
        return JSONResponse(
            status_code=400,
            content={"error": f"Libro no disponible: {exc}"}
        )

    @app.exception_handler(LibraryFullError)
    async def library_full_handler(request: Request, exc: LibraryFullError):
        return JSONResponse(
            status_code=400,
            content={"error": "La biblioteca ya alcanzó su límite de préstamos"}
        )