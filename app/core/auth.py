import time
from typing import Optional

import jwt

from fastapi.openapi.models import HTTPBearer as HTTPBearerModel
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.datastructures import Headers
from starlette.requests import Request

from app.core.config import get_app_settings

settings = get_app_settings()


class JWTPossible(SecurityBase):
    def __init__(self):
        self.model = HTTPBearerModel(bearerFormat=settings.authjwt_header_type, description="JWT header token type")
        self.scheme_name = self.__class__.__name__
        super(JWTPossible, self).__init__()

    async def __call__(self, request: Request) -> Optional[str]:
        token: Optional[str] = self.get_token_from_header(request.headers)
        if token is None:
            return None

        decoded_token: Optional[dict] = self.decode_token(token)
        if decoded_token is None:
            return None

        return decoded_token.get('sub', None)

    @classmethod
    def get_token_from_header(cls, headers: Headers) -> Optional[str]:
        authorization: str = headers.get(settings.authjwt_header_name)
        if authorization is None:
            return None

        scheme, credentials = get_authorization_scheme_param(authorization)

        if scheme.lower() != settings.authjwt_header_type.lower():
            return None

        return credentials if credentials else None

    @classmethod
    def decode_token(cls, token: str) -> Optional[dict]:
        try:
            decoded_token = jwt.decode(token, settings.authjwt_secret_key, algorithms=[settings.authjwt_algorithm])
            return decoded_token if decoded_token["exp"] >= time.time() else None
        except (jwt.PyJWTError, KeyError):
            return None
