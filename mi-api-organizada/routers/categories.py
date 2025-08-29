from fastapi import APIRouter
from services import book_service
from utils.responses import success_response

router = APIRouter()

@router.get("/")
def list_categories():
    genres = set([book.genre for book in book_service.get_books() if book.genre])
    return success_response(list(genres))

@router.get("/{genre}/books")
def books_by_genre(genre: str):
    books = [b for b in book_service.get_books() if b.genre == genre]
    return success_response(books)