from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Body, HTTPException
from jwt import InvalidIssuerError

from app import resources
from app.api.dependencies.database import get_repository
from app.api.dependencies.shelves import ShelfFilterManager
from app.api.dependencies.user import require_user, possible_user
from app.db.queries.tables import User
from app.db.repositories.books.books import BookRepository
from app.db.repositories.shelves.shelves import ShelfRepository
from app.db.repositories.shelves.tag import ShelfTagsRepository
from app.models.schemas.comments import ListOfCommentsInResponse, CommentInResponse, CommentInCreate
from app.models.schemas.common import SuccessDelete, SuccessUpdate
from app.models.schemas.shelves import ShelfForCreate, ShelfInResponse, ListOfShelvesInResponse, ShelfFilter, \
    ShelfRateInResponse, ShelfRateInCreate, BookInShelfInResponse, BookInShelfInCreate, BookInShelfInUpdate
from app.models.schemas.tags import TagsInList

router = APIRouter()

shelf_filter_manager = ShelfFilterManager(['name', 'created_at'])


@router.get("/tags", response_model=TagsInList, name="shelves:shelf-tags")
async def get_all_tags(
        tags_repo: ShelfTagsRepository = Depends(get_repository(ShelfTagsRepository)),
) -> TagsInList:
    tags = await tags_repo.get_all_shelf_tags()
    return TagsInList(tags=tags)


@router.get("/", response_model=ListOfShelvesInResponse, name="shelves:filter-shelves")
async def filter_shelves(
        shelf_filter: ShelfFilter = Depends(shelf_filter_manager),
        user: Optional[User] = Depends(possible_user),
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository))
) -> ListOfShelvesInResponse:
    shelves = await shelf_repo.filter_shelves(
        tags=shelf_filter.tags,
        sort_by=shelf_filter.sort_by,
        user=user,
        offset=shelf_filter.offset,
        limit=shelf_filter.limit,
        _type='public'
    )

    return ListOfShelvesInResponse(shelves=shelves)


@router.get("/{shelf_uid}/", response_model=ShelfInResponse, name="shelves:retrieve")
async def retrieve_shelf(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        user: Optional[User] = Depends(possible_user),
) -> ShelfInResponse:
    shelf = await shelf_repo.get_shelf_by_uid(shelf_uid=shelf_uid)
    if shelf.type == 'private':
        if user is None:
            raise InvalidIssuerError(resources.PRIVATE_SHELF_ACCESS_DENIED)
        elif shelf.user_uid != user.uid:
            raise InvalidIssuerError(resources.PRIVATE_SHELF_ACCESS_DENIED)

    return ShelfInResponse(shelf=shelf)


@router.post("/", response_model=ShelfInResponse, name="shelves:create-shelf")
async def create_shelf(
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user),
        book_data: ShelfForCreate = Body(..., embed=True, alias='shelf')
) -> ShelfInResponse:
    book_ids = await book_repo.get_existing_book(book_ids=book_data.books, only_ids=True)

    shelf = await shelf_repo.create_shelf(
        user=required_user,
        name=book_data.name,
        description=book_data.description,
        tags=book_data.tags,
        _type=book_data.type,
        book_ids=book_ids
    )

    return ShelfInResponse(shelf=shelf)


@router.post("/{shelf_uid}/rate/", response_model=ShelfRateInResponse, name="shelves:rate-shelf")
async def rate_shelf(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user),
        rate: ShelfRateInCreate = Body(..., embed=True, alias="rate")
) -> ShelfRateInResponse:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    existing_rate = await shelf_repo.get_rate(user=required_user, shelf=shelf)
    if existing_rate is not None:
        raise HTTPException(status_code=404, detail=resources.RATE_ALREADY_EXISTS)

    rate_obj = await shelf_repo.rate_shelf(user=required_user, shelf=shelf, rate=rate.rate)

    return ShelfRateInResponse(rate=rate_obj)


@router.delete("/{shelf_uid}/rate/", response_model=SuccessDelete, name="shelves:remove-shelf-rate")
async def remove_rate_shelf(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user)
) -> SuccessDelete:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_NOT_FOUND)

    rate = await shelf_repo.get_rate(shelf=shelf, user=required_user)
    if rate is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    await shelf_repo.delete_rate(rate=rate)
    return SuccessDelete()


@router.get("/{shelf_uid}/comments/", response_model=ListOfCommentsInResponse, name="shelves:shelf-comments")
async def get_comments(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository))
) -> ListOfCommentsInResponse:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    comments = await shelf_repo.get_comments(shelf)
    return ListOfCommentsInResponse(comments=comments)


@router.post("/{shelf_uid}/comments/", response_model=CommentInResponse, name="shelves:add-comment")
async def add_comment(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user),
        comment: CommentInCreate = Body(..., embed=True, alias="comment")
) -> CommentInResponse:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    comment_obj = await shelf_repo.create_comment(user=required_user, shelf=shelf, content=comment.content)

    return CommentInResponse(comment=comment_obj)


@router.delete("/{shelf_uid}/comments/{comment_id}/", response_model=SuccessDelete, name="shelves:delete-comment")
async def delete_comment(
        shelf_uid: UUID,
        comment_id: int,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user)
) -> SuccessDelete:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    comment = await shelf_repo.get_comment_by_id(comment_id)
    if comment is None:
        raise HTTPException(status_code=404, detail=resources.COMMENT_NOT_FOUND)
    if comment.shelf_uid != shelf.uid:
        raise HTTPException(status_code=400, detail=resources.COMMENT_DOES_NOT_BELONG_BOOK)
    if comment.user_uid != required_user.uid:
        raise HTTPException(status_code=400, detail=resources.COMMENT_DOES_NOT_BELONG_USER)

    await shelf_repo.delete_comment(comment)

    return SuccessDelete()


@router.post("/{shelf_uid}/books-in-shelf/", response_model=BookInShelfInResponse, name="shelves:add-book-to-shelf")
async def add_book_to_shelf(
        shelf_uid: UUID,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        book_repo: BookRepository = Depends(get_repository(BookRepository)),
        required_user: User = Depends(require_user),
        book_data: BookInShelfInCreate = Body(..., embed=True, alias='book')
) -> BookInShelfInResponse:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    book = await book_repo.get_book_instance_by_id(book_id=book_data.book_id)

    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)
    if book is None:
        raise HTTPException(status_code=400, detail=resources.BOOK_NOT_FOUND)

    if shelf.user_uid != required_user.uid:
        raise HTTPException(status_code=403, detail=resources.SHELF_ACCESS_DENIED)

    book_in_shelf = await shelf_repo.add_book(shelf=shelf, book=book)
    return BookInShelfInResponse(book_in_shelf=book_in_shelf)


@router.delete("/{shelf_uid}/books-in-shelf/{book_in_shelf_id}", response_model=SuccessDelete,
               name="shelves:remove-book-from-shelf")
async def remove_book_from_shelf(
        shelf_uid: UUID,
        book_in_shelf_id: int,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user),
) -> SuccessDelete:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid=shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    book_in_shelf = await shelf_repo.get_book_in_shelf_by_id(book_in_shelf_id=book_in_shelf_id)
    if book_in_shelf is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_IN_SHELF_NOT_FOUND)

    if book_in_shelf.shelf_uid != shelf.uid:
        raise HTTPException(status_code=400, detail=resources.BOOK_DOES_BELONG_TO_SHELF)

    if shelf.user_uid != required_user.uid:
        raise HTTPException(status_code=403, detail=resources.SHELF_ACCESS_DENIED)

    await shelf_repo.delete_book_in_shelf(book_in_shelf)

    return SuccessDelete()


@router.put("/{shelf_uid}/books-in-shelf/{book_in_shelf_id}/", response_model=BookInShelfInResponse,
            name="shelves:update-book-in-shelf"
            )
async def update_book_in_shelf(
        shelf_uid: UUID,
        book_in_shelf_id: int,
        shelf_repo: ShelfRepository = Depends(get_repository(ShelfRepository)),
        required_user: User = Depends(require_user),
        book_in_shelf_data: BookInShelfInUpdate = Body(..., embed=True, alias='book_in_shelf')
) -> BookInShelfInResponse:
    shelf = await shelf_repo.get_shelf_instance_by_uid(shelf_uid)
    if shelf is None:
        raise HTTPException(status_code=404, detail=resources.SHELF_NOT_FOUND)

    book_in_shelf = await shelf_repo.get_book_in_shelf_by_id(book_in_shelf_id=book_in_shelf_id)
    if book_in_shelf is None:
        raise HTTPException(status_code=404, detail=resources.BOOK_IN_SHELF_NOT_FOUND)

    if book_in_shelf.shelf_uid != shelf.uid:
        raise HTTPException(status_code=400, detail=resources.BOOK_DOES_BELONG_TO_SHELF)

    if shelf.user_uid != required_user.uid:
        raise HTTPException(status_code=403, detail=resources.SHELF_ACCESS_DENIED)

    book_in_shelf = await shelf_repo.change_book_in_shelf(book_in_shelf=book_in_shelf,
                                                          tags=set(book_in_shelf_data.tags))

    return BookInShelfInResponse(book_in_shelf=book_in_shelf)
