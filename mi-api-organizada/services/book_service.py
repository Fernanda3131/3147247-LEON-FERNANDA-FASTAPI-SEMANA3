from exceptions.custom_exceptions import (
    BookNotFoundError, DuplicateISBNError,
    InvalidBookDataError, BookNotAvailableError,
    LibraryFullError
)
from models.book import Book

# 📚 "Base de datos" simulada
books = [
    Book(
        id=1,
        title="1984",
        author="George Orwell",
        isbn="123456789",
        is_available=True,
        rating=4.8,
        year=1949,
        price=39.99
    ),
    Book(
        id=2,
        title="Cien años de soledad",
        author="Gabriel García Márquez",
        isbn="987654321",
        is_available=True,
        rating=4.9,
        year=1967,
        price=29.99
    )
]

borrowed_books_count = 0
MAX_BORROWED = 10

def get_books():
    """Devuelve todos los libros."""
    return books

def get_book_by_id(book_id: int):
    """Busca un libro por ID."""
    for book in books:
        if book.id == book_id:
            return book
    raise BookNotFoundError(book_id)

def add_book(new_book: Book):
    """Agrega un nuevo libro, validando ISBN único."""
    for book in books:
        if book.isbn == new_book.isbn:
            raise DuplicateISBNError(new_book.isbn)
    books.append(new_book)
    return {"message": f"Libro '{new_book.title}' agregado con éxito."}

def borrow_book(book_id: int):
    global borrowed_books_count
    book = get_book_by_id(book_id)

    if not book.is_available:
        raise BookNotAvailableError(book_id)

    if borrowed_books_count >= MAX_BORROWED:
        raise LibraryFullError()

    if hasattr(book, "is_bestseller") and book.is_bestseller:
        raise InvalidBookDataError("Los bestsellers solo se pueden leer en sala.")

    book.is_available = False
    borrowed_books_count += 1
    return {"message": f"Libro '{book.title}' prestado con éxito."}

def return_book(book_id: int):
    global borrowed_books_count
    book = get_book_by_id(book_id)

    if book.is_available:
        raise InvalidBookDataError("El libro no estaba prestado.")

    book.is_available = True
    borrowed_books_count -= 1
    return {"message": f"Libro '{book.title}' devuelto con éxito."}

def search_books(query: str):
    if not query or len(query) < 3:
        raise InvalidBookDataError("El término de búsqueda debe tener al menos 3 caracteres.")

    results = [book for book in books if query.lower() in book.title.lower()]
    if not results:
        raise BookNotFoundError(query)
    return results