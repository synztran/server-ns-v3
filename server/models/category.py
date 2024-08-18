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
    category_id: str = Field(...)
    # category_url_name: str
    slug: str
    category_name: str
    manufacturing: str
    author: str
    proxy_host: str
    status_gb: StatusGB
    type: CategoryType
    date_start: str
    date_end: str
    date_payment: str
    min_price: int
    max_price: int
    tax: int
    handle: int
    thumbnail: Image
    pic_list: List[Image]
    pic_profile: Image
    content: str
    time_line: None
    is_active: bool = False
    description: str = None
    collapse_content: CollapseContent
    sale_price: int = 0
    is_active: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 'abc',
                # "category_url_name": "123456abc",
                "slug": "abc",
                "category_name": "Hari",
                "manufacturing": "Chan",
                "author": "A Lu",
                "proxy_host": "text",
                "status_gb": StatusGB.TBA,
                "type": 0,
                "date_start": '',
                "date_end": '',
                "date_payment": '',
                "min_price": 0,
                "max_price": 0,
                "tax": 0,
                "handle": 0,
                "thumbnail": {
                    "path": "",
                    "size": 0
                },
                "pic_list": [],
                "pic_profile": {
                    "path": "",
                    "size" : 0
                },
                "content":  "",
                "get_noti": False,
                "time_line": {},
                "is_active": False,
                "description": "",
                "collapse_content": [],
                "sale_price": 0,
                "is_active": False
            }
        }


class ParamsGet(BaseModel):
    status_gb: Optional[str] = ""
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
