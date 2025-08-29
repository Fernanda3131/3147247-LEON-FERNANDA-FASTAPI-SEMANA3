import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_create_and_list_books():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Crear un libro
        response = await client.post("/api/v1/books/", json={
            "id": 1,
            "title": "1984",
            "author": "George Orwell",
            "rating": 4.5,
            "bestseller": True,
            "tags": ["dystopia"],
            "year": 1949,
            "price": 20,
            "is_available": True
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "1984"

        # Listar libros
        response = await client.get("/api/v1/books/")
        assert response.status_code == 200
        books = response.json()["data"]
        assert len(books) > 0
