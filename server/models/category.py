from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class StatusGB(Enum):
    INSTOCK = "INSTOCK"
    OUTSOTCK = "OUTSOTCK"
    GB = "GB"
    TBA = "TBA"
    ALL = ""

class CategoryType(Enum):
    TBA = "TBD"
    KEYBOARD = "KEYBOARD",
    SWITCH = "SWITCH",
    KEYCAP = "KEYCAP",
    ACCESSORY = "ACCESSORY",

class Image(BaseModel):
    path: str
    size: float

class CollapseContent(BaseModel):
    title: str
    content: str

class CategorySchema(BaseModel):
    categoryId: str = Field(...)
    slug: str
    categoryName: str
    manufacturing: str
    author: str
    proxyHost: str
    statusGb: StatusGB
    type: CategoryType
    dateStart: str
    dateEnd: str
    datePayment: str
    minPrice: int
    maxPrice: int
    tax: int
    handle: int
    thumbnail: Image
    picList: List[Image]
    picProfile: Image
    content: str
    timeLine: None
    isActive: bool = False
    description: str = None
    collapseContent: CollapseContent
    salePrice: int = 0
    isActive: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "categoryId": 'abc',
                "slug": "abc",
                "categoryName": "Hari",
                "manufacturing": "Chan",
                "author": "A Lu",
                "proxyHost": "text",
                "statusGb": StatusGB.TBA,
                "type": 0,
                "dateStart": '',
                "dateEnd": '',
                "datePayment": '',
                "minPrice": 0,
                "maxPrice": 0,
                "tax": 0,
                "handle": 0,
                "thumbnail": {
                    "path": "",
                    "size": 0
                },
                "picList": [],
                "picProfile": {
                    "path": "",
                    "size" : 0
                },
                "content":  "",
                "getNoti": False,
                "timeLine": {},
                "isActive": False,
                "description": "",
                "collapseContent": [],
                "salePrice": 0,
                "isActive": False
            }
        }

class ParamsGet(BaseModel):
    statusGb: Optional[str] = ""
    slug: Optional[str] = ""
    ids: Optional[List[str]] = []

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": "OK"
    }

def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
