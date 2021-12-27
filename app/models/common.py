from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class DateTimeModelMixin(BaseModel):
    # created_at: Optional[datetime] = None
    # updated_at: Optional[datetime] = None

    # @validator("created_at", "updated_at", pre=True)
    # def default_datetime(
    #         cls,  # noqa: N805
    #         value: datetime,  # noqa: WPS110
    # ) -> datetime:
    #     return value or datetime.now()
    ...


class IDModelMixin(BaseModel):
    id_: int = Field(0, alias="id")
