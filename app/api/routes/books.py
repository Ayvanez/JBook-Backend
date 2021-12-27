import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.books import BookFilterManager
from app.api.dependencies.database import get_repository
from app.api.dependencies.user import require_user, possible_user
from app.db.queries.tables import User

from app.db.repositories.books.authors import BookAuthorRepository
from app.db.repositories.books.categories import BookCategoryRepository
from app.db.repositories.books.tags import BookTagsRepository
from app.db.repositories.books.publishers import BookPublisherRepository
from app.db.repositories.books.books import BookRepository
from app.models.schemas.comments import CommentInResponse, CommentInCreate, ListOfCommentsInResponse
from app.models.schemas.common import SuccessDelete
from app.models.schemas.tags import TagsInList
from app.models.schemas.books import ListOfBookPublisherInResponse, ListOfBooksInResponse, BooksFilter, \
    BookInResponse, ListOfBookAuthorInResponse, ListOfBookCategoriesInResponse, BookRateInCreate, BookRateInResponse
from app import resources

router = APIRouter()

book_filter_manager = BookFilterManager(['title', 'rate', 'pub_date', 'created_at'])


@router.get("/tags/", response_model=TagsInList, name="books:book-tags")
async def get_all_tags(
        tags_repo: BookTagsRepository = Depends(get_repository(BookTagsRepository)),
) -> TagsInList:
    tags = await tags_repo.get_all_book_tags()
    return TagsInList(tags=tags)


@router.get("/publishers/", response_model=ListOfBookPublisherInResponse, name="books:book-publishers")
async def get_all_tags(
        publisher_repo: BookPublisherRepository = Depends(get_repository(BookPublisherRepository)),
) -> ListOfBookPublisherInResponse:
    publishers = await publisher_repo.get_all_publishers()
    return ListOfBookPublisherInResponse(publishers=publishers)


@router.get("/authors/", response_model=ListOfBookAuthorInResponse, name="books:book-authors")
async def get_all_tags(
        author_repo: BookAuthorRepository = Depends(get_repository(BookAuthorRepository)),
) -> ListOfBookAuthorInResponse:
    authors = await author_repo.get_all_authors()
    return ListOfBookAuthorInResponse(authors=authors)


@router.get("/categories/", response_model=ListOfBookCategoriesInResponse, name="books:book-categories")
async def get_all_tags(
        category_repo: BookCategoryRepository = Depends(get_repository(BookCategoryRepository)),
) -> ListOfBookCategoriesInResponse:
    categories = await category_repo.get_all_categories()
    return ListOfBookCategoriesInResponse(categories=categories)


@router.get("/", response_model=ListOfBooksInResponse, name="books:filter-books")
async def filter_books(
        books_filter: BooksFilter = Depends(book_filter_manager),
        user: Optional[User] = Depends(possible_user),
        book_repo: BookRepository = Depends(get_repository(BookRepository))
) -> ListOfBooksInResponse:
    books = await book_repo.filter_books(
        tags=books_filter.tags,
        categories=books_filter.categories,
        publishers=books_filter.publishers,
        user=user,
        authors=books_filter.authors,
        sort_by=books_filter.sort_by,
        offset=books_filter.offset,
        limit=books_filter.limit,
    )

    return ListOfBooksInResponse(books=books)


@router.get("/{book_id}/", response_model=BookInResponse, name="books:retrieve")
async def retrieve_book(
        book_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository))
) -> BookInResponse:
    book = await book_repo.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    return BookInResponse(book=book)


@router.get("/{book_id}/comments/", response_model=ListOfCommentsInResponse, name="books:book-comments")
async def get_comments(
        book_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository))
) -> ListOfCommentsInResponse:
    book = await book_repo.get_book_instance_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    comments = await book_repo.get_comments(book)
    return ListOfCommentsInResponse(comments=comments)


@router.post("/{book_id}/comments/", response_model=CommentInResponse, name="books:add-comment")
async def add_comment(
        book_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user),
        comment: CommentInCreate = Body(..., embed=True, alias="comment")
) -> CommentInResponse:
    book = await book_repo.get_book_instance_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    comment_obj = await book_repo.create_comment(user=required_user, book=book, content=comment.content)

    return CommentInResponse(comment=comment_obj)


@router.delete("/{book_id}/comments/{comment_id}/", response_model=SuccessDelete, name="books:delete-comment")
async def delete_comment(
        book_id: int,
        comment_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user)
) -> SuccessDelete:
    book = await book_repo.get_book_instance_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    comment = await book_repo.get_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail=resources.COMMENT_NOT_FOUND)
    if comment.book_id != book.id:
        raise HTTPException(status_code=400, detail=resources.COMMENT_DOES_NOT_BELONG_BOOK)
    if comment.user_uid != required_user.uid:
        raise HTTPException(status_code=400, detail=resources.COMMENT_DOES_NOT_BELONG_USER)

    await book_repo.delete_comment(comment)

    return SuccessDelete()


@router.post("/{book_id}/rate/", response_model=BookRateInResponse, name="books:rate-book")
async def rate_book(
        book_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user),
        rate: BookRateInCreate = Body(..., embed=True, alias="rate")
) -> BookRateInResponse:
    book = await book_repo.get_book_instance_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    existing_rate = await book_repo.get_rate(user=required_user, book=book)
    if existing_rate is not None:
        raise HTTPException(status_code=404, detail=resources.RATE_ALREADY_EXISTS)

    rate_obj = await book_repo.rate_book(user=required_user, book=book, rate=rate.rate)

    return BookRateInResponse(rate=rate_obj)


@router.delete("/{book_id}/rate/", response_model=SuccessDelete, name="books:remove-book-rate")
async def remove_book_rate(
        book_id: int,
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user)
) -> SuccessDelete:
    book = await book_repo.get_book_instance_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    rate = await book_repo.get_rate(book=book, user=required_user)
    if rate is None:
        raise HTTPException(status_code=404, detail=resources.RATE_NOT_FOUND)

    await book_repo.delete_rate(rate=rate)
    return SuccessDelete()
