from typing import Optional

from app.models.domain.rwmodel import RWModel


class User(RWModel):
    first_name: Optional[str]
    surname: Optional[str]
