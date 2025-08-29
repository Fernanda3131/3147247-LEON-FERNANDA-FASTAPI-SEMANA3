from exceptions.custom_exceptions import BookNotAvailableError, LibraryFullError
from services.book_service import get_book_by_id

active_borrowings = []
MAX_BORROWINGS = 10

def borrow_book(book_id: int, user_id: int):
    if len(active_borrowings) >= MAX_BORROWINGS:
        raise LibraryFullError("No se pueden prestar más de 10 libros simultáneamente")

    book = get_book_by_id(book_id)

    if not book.is_available:
        raise BookNotAvailableError(f"El libro '{book.title}' no está disponible")

    book.is_available = False
    active_borrowings.append({"book_id": book.id, "user_id": user_id})
    return {"book_id": book.id, "title": book.title}

def return_book(book_id: int, user_id: int):
    book = get_book_by_id(book_id)
    for borrow in active_borrowings:
        if borrow["book_id"] == book_id and borrow["user_id"] == user_id:
            active_borrowings.remove(borrow)
            book.is_available = True
            return {"book_id": book.id, "title": book.title}
    return {"message": "El préstamo no existe"}