from app.models.schemas.rwschema import RWSchema


class SuccessDelete(RWSchema):
    states: str = 'success'


class SuccessUpdate(RWSchema):
    status: str = 'success'
