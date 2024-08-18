from pydantic import BaseModel, Field
from typing import List


class Image(BaseModel):
    path: str
    size: float


class CollectionSchema(BaseModel):
    collection_id: str = Field(...)
    category_id: List[str]
    collection_name: str
    is_active: bool
    min_price: int
    max_pirce: int
    thumbnail: Image
    image_list: List[Image]
    description: str

    class Config:
        json_schema_extra = {
            "example": {
                "collection_id": 'abc',
                "collection_name": "abc",
                "category_id": ['1', '2'],
                "min_price": 0,
                "max_price": 0,
                "thumbnail": {
                    "path": "",
                    "size": 0
                },
                "image_list": [{"paht": "", "size": 0}],
                "description":  "",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": "OK"
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
