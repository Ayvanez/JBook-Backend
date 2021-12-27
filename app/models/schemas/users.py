from app.models.domain.users import User
from app.models.schemas.rwschema import RWSchema


class UserForResponse(User, RWSchema):
    ...


class UserInResponse(RWSchema):
    user: UserForResponse
