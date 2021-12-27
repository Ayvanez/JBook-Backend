from fastapi import APIRouter

from app.api.routes.books import router as book_router

router = APIRouter()
router.include_router(book_router, tags=["books"], prefix="/books")
