from typing import List

from app.models.domain.users import User
from app.models.schemas.rwschema import RWSchema


class CommentForResponse(RWSchema):
    user: User
    content: str


class ListOfCommentsInResponse(RWSchema):
    comments: List[CommentForResponse]


class CommentInResponse(RWSchema):
    comment: CommentForResponse


class CommentInCreate(RWSchema):
    content: str
