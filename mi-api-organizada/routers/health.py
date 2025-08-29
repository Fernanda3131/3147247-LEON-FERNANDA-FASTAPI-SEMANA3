# routers/health.py
from fastapi import APIRouter
from utils.responses import success_response

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
def health_check():
    return success_response(
        {"status": "healthy"},
        message="API is running"
    )