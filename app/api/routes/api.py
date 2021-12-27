from fastapi import APIRouter

from app.api.routes.books import router as book_router
from app.api.routes.shelves import router as shelf_router

router = APIRouter()
router.include_router(book_router, tags=["books"], prefix="/books")
router.include_router(shelf_router, tags=["shelves"], prefix="/shelves")
