from fastapi import APIRouter
from services import borrowing_service
from utils.responses import success_response

router = APIRouter()

@router.post("/borrow/{book_id}")
def borrow_book(book_id: int, user_id: int = 1):  # user_id simulado
    result = borrowing_service.borrow_book(book_id, user_id)
    return success_response(result, "Book borrowed successfully")

@router.post("/return/{book_id}")
def return_book(book_id: int, user_id: int = 1):
    result = borrowing_service.return_book(book_id, user_id)
    return success_response(result, "Book returned successfully")

@router.get("/active")
def active_borrowings():
    return success_response(borrowing_service.active_borrowings)