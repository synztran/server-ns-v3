from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from server.models.category import CategoryType


class CartProduct(BaseModel):
    type: str = 'product'
    productId: str
    # sku: str
    quantity: int
    price: float
    total: float
    options: Optional[dict] = []

class CartService(BaseModel):
    type: str = 'service'
    serviceId: Optional[str] = None
    # sku: str
    quantity: int
    price: float
    total: float
    options: Optional[dict] = []

class CartFees(BaseModel):
    shipping: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    handling: Optional[float] = 0.0
    voucherCode: Optional[str] = None
    voucherDiscount: Optional[float] = None

class CartProductSchema(BaseModel):
    type: str
    productId: str
    productName: str
    sellerName: str
    quantity: int
    price: float
    cartId: Optional[str] = None
    # page: str
    categoryId: str
    categoryName: Optional[str] = None
    image: Optional[str] = None
    slug: Optional[str] = None

class RemoveCartItemSchema(BaseModel):
    cartId: str
    productId: str

class UpdateCartProduct(BaseModel):
    cartId: str
    productId: str
    quantity: int

class CartSchema(BaseModel):
    customerId: int
    cartId: str
    products: List[CartProductSchema] = []
    services: List[CartService] = []
    fees: CartFees 
    totalPrice: float = 0
    updateAt: datetime
    totalProductQuantity: int = 0


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": "OK"
    }

def ErrorResponseModel(code, message):
    return {
        "status": "Error",
        "code": code,
        "message": message,
        "status": "Error"
    }

def ResponeSuccessMessage(message):
    return {
        "status": "OK",
        "code": 200,
        "message": message
    }