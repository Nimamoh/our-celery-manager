from enum import StrEnum
from our_celery_manager.app.models.dtos import OCMBaseModel

class Type(StrEnum):
    STUB = "STUB"

class WsModel(OCMBaseModel):
    _type: Type

    def __init__(self, type: Type, **data):
        self._type = type
        super.__init__(**data)


class StubModel(WsModel):

    content: str
    
    def __init__(self, **data):
        super.__init__(Type.STUB, **data)
