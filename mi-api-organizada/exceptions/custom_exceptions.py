class BookNotFoundError(Exception):
    def __init__(self, book_id: int):
        self.message = f"El libro con ID {book_id} no fue encontrado."
        super().__init__(self.message)

class DuplicateISBNError(Exception):
    def __init__(self, isbn: str):
        self.message = f"Ya existe un libro con el ISBN {isbn}."
        super().__init__(self.message)

class InvalidBookDataError(Exception):
    def __init__(self, details: str):
        self.message = f"Datos inválidos del libro: {details}"
        super().__init__(self.message)

class BookNotAvailableError(Exception):
    def __init__(self, book_id: int):
        self.message = f"El libro con ID {book_id} no está disponible."
        super().__init__(self.message)

class LibraryFullError(Exception):
    def __init__(self):
        self.message = "No se pueden prestar más de 10 libros simultáneamente."
        super().__init__(self.message)