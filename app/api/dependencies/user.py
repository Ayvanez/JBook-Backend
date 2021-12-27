import time
from typing import Optional

import jwt
from fastapi import Depends


from fastapi_jwt_auth import AuthJWT
from starlette.datastructures import Headers
from starlette.requests import Request

from app.api.dependencies.database import get_repository
from app.core.auth import JWTPossible
from app.core.config import get_app_settings
from app.db.queries.tables import User
from app.db.repositories.users import UsersRepository


async def require_user(
        authorize: AuthJWT = Depends(),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
) -> User:
    authorize.jwt_required()

    user_uid = authorize.get_jwt_subject()
    user_params: dict = authorize.get_raw_jwt()['user']
    _user = await user_repo.get_or_create_user(user_uid=user_uid, **user_params)

    return _user


async def possible_user(
        authorized_sub: Optional[str] = Depends(JWTPossible()),
        user_repo: UsersRepository = Depends(get_repository(UsersRepository))
):
    _user = await user_repo.get_user_id_exists(authorized_sub)
    return _user
