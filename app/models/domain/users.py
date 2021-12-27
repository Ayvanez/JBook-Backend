from typing import Optional

from app.models.common import IDModelMixin
from app.models.domain.rwmodel import RWModel


class User(RWModel, IDModelMixin):
    username: str
    status: Optional[str] = None
