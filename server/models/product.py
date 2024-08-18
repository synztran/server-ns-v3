from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


from server.models.productOption import ProductOptionSchema


class ProductPart(Enum):
    CASE = "CASE",
    PLATE = "PLATE",
    PCB = "PCB",
    ACCESSORIES = "ACCESSORIES",
    KEYCAP = "KEYCAP",
    SWITCH = "SWITCH",
    ARTISAN = "ARTISAN",
    ETC = "ETC"


class ProductType(Enum):
    COMBO = 0,
    PART = 1

class Material(Enum):
    ABS = 0,
    PBT = 1,
    POM = 2,
    FR4 = 3,
    TBD = 5


class IImage(BaseModel):
    path: str
    size: float


class ProductSchema(BaseModel):
    product_id: str = Field(...)
    product_name: str
    replace_product_name: str
    category_id: str
    # category_url_name: str
    slug: str
    # product_accessory: 0 = Keeb Top Case | 1 = Keeb Bot case | 2 = Keeb Plate | 3 = Keeb Frame | 4 = keycap | 5 = switches | 7 = artisan | 8 = etc
    product_part: ProductPart = None
    outstock: bool = False
    price: float
    pic_product: IImage
    pic_list: List[IImage]
    specs: str
    product_type: ProductType
    productOpts: List[ProductOptionSchema]

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
