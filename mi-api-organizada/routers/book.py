from fastapi import APIRouter, Query
from models.book import Book
from services.book_service import (
    get_books,
    add_book,
    borrow_book,
    return_book,
    search_books
)
from utils.responses import success_response

router = APIRouter(prefix="/api/v1/books", tags=["Books"])

# 📚 Listar libros
@router.get("/")
def list_books():
    
    return success_response(get_books())

# ➕ Crear libro
@router.post("/")
def create_book(book: Book):
    new_book = add_book(book)
    return success_response(new_book, "Book created successfully")

# 🔍 Búsqueda avanzada
@router.get("/search")
def search(
    title: str = Query(None),
    author: str = Query(None),
    genre: str = Query(None),
    year_from: int = Query(None),
    year_to: int = Query(None),
    available_only: bool = Query(False)
):
    results = search_books(
        title=title,
        author=author,
        genre=genre,
        year_from=year_from,
        year_to=year_to,
        available_only=available_only
    )
    return success_response(results)

# 📖 Prestar libro
@router.post("/{book_id}/borrow")
def borrow(book_id: int):
    return borrow_book(book_id)

# 📖 Devolver libro
@router.post("/{book_id}/return")
def return_book_endpoint(book_id: int):
    return return_book(book_id)