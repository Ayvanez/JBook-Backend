from fastapi import APIRouter, Depends, HTTPException, Body

from app.api.dependencies.books import BookFilterManager
from app.api.dependencies.database import get_repository
from app.db.queries.tables import User
from app.db.repositories.books.authors import BookAuthorRepository
from app.db.repositories.books.categories import BookCategoryRepository
from app.db.repositories.books.tags import BookTagsRepository
from app.db.repositories.books.publishers import BookPublisherRepository
from app.db.repositories.books.books import BookRepository
from app.models.schemas.comments import CommentInResponse, CommentInCreate
from app.models.schemas.tags import TagsInList
from app.models.schemas.books import ListOfBookPublisherInResponse, ListOfBooksInResponse, BooksFilter, BookInResponse, \
    ListOfBookAuthorInResponse, ListOfBookCategoriesInResponse, BookRateInCreate

router = APIRouter()

book_filter_manager = BookFilterManager(['name', 'rate', 'pub_date', 'created_at'])


@router.get("/tags", response_model=TagsInList, name="books:get-all-tags")
async def get_all_tags(
        tags_repo: BookTagsRepository = Depends(get_repository(BookTagsRepository)),
) -> TagsInList:
    tags = await tags_repo.get_all_book_tags()
    return TagsInList(tags=tags)


@router.get("/publishers", response_model=ListOfBookPublisherInResponse, name="books:get-all-publishers")
async def get_all_tags(
        publisher_repo: BookPublisherRepository = Depends(get_repository(BookPublisherRepository)),
) -> ListOfBookPublisherInResponse:
    publishers = await publisher_repo.get_all_publishers()
    return ListOfBookPublisherInResponse(publishers=publishers)


@router.get("/authors", response_model=ListOfBookAuthorInResponse, name="books:get-all-authors")
async def get_all_tags(
        author_repo: BookAuthorRepository = Depends(get_repository(BookAuthorRepository)),
) -> ListOfBookAuthorInResponse:
    authors = await author_repo.get_all_authors()
    return ListOfBookAuthorInResponse(authors=authors)


@router.get("/categories", response_model=ListOfBookCategoriesInResponse, name="books:get-all-categories")
async def get_all_tags(
        category_repo: BookCategoryRepository = Depends(get_repository(BookAuthorRepository)),
) -> ListOfBookCategoriesInResponse:
    categories = await category_repo.get_all_categories()
    return ListOfBookCategoriesInResponse(categories=categories)


@router.get("", response_model=ListOfBooksInResponse, name="books:filter-books")
async def filter_books(
        books_filter: BooksFilter = Depends(book_filter_manager),
        book_repo: BookRepository = Depends(get_repository(BookRepository))
) -> ListOfBooksInResponse:
    books = await book_repo.filter_books(
        tags=books_filter.tags,
        categories=books_filter.categories,
        publishers=books_filter.publishers,
        authors=books_filter.authors,
        sort_by=books_filter.sort_by,
        offset=books_filter.offset,
        limit=books_filter.limit,
    )
    return ListOfBooksInResponse(books=books)


@router.get("/{book_id}", response_model=BookInResponse, name="books:retrieve")
async def retrieve_book(book_id: int,
                        book_repo: BookRepository = Depends(get_repository(BookRepository))) -> BookInResponse:
    book = await book_repo.get_book_by_id(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookInResponse(book=book)


@router.get("/{book_id}/comments", response_model=CommentInResponse, name="books:comments")
async def get_comments(book_id: int,
                       book_repo: BookRepository = Depends(get_repository(BookRepository))) -> CommentInResponse:
    comments = book_repo.get_comments_by_book_id(book_id)
    return CommentInResponse(comments=comments)


@router.post("/{book_id}/comments", name="books:add-comment")
async def add_comment(book_id: int,
                      book_repo: BookRepository = Depends(get_repository(BookRepository)),
                      comment: CommentInCreate = Body(..., embed=True, alias="comment"), ):
    await book_repo.create_comment(user=User(), book_id=book_id, content=comment.content)


@router.delete("/{book_id}/comments", name="books:delete-comment")
async def delete_comment(book_id: int, book_repo: BookRepository = Depends(get_repository(BookRepository))):
    await book_repo.delete_comment(user=User(), book_id=book_id)


@router.post("/{book_id}/rate", name="books:rate-book")
async def rate_book(book_id: int, book_repo: BookRepository = Depends(get_repository(BookRepository)),
                    rate: BookRateInCreate = Body(..., embed=True, alias="rate")):
    await book_repo.rate_book(user=User(), book_id=book_id, rate=rate.rate)


