from bson import ObjectId
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


class IImage(BaseModel):
    path: str
    size: float


class ENUM_STATUS(Enum):
    OUTSTOCK = 0,
    INSTOCK = 1

class ParamsGet(BaseModel):
    ids: Optional[List[str]] = []

class ProductOptionSchema(BaseModel):
    productOptionID: str = Field(...)
    product_id: str
    productOptionName: str
    productOptionPrice: float
    imageUrl: IImage
    status: ENUM_STATUS
    quantity: int

    class Config:
        json_schema_extra = {
            "example": {

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
    return {
        "error": error,
        "code": code,
        "message": message
    }
