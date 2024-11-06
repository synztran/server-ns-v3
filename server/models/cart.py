from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from server.models.category import CategoryType


# class CartProduct(BaseModel):
#     type: Optional[str] = 'product'
#     productId: str
#     quantity: int
#     price: float
#     total: float
#     options: Optional[dict] = []
#     productType: str

class CartService(BaseModel):
    type: str = 'service'
    serviceId: Optional[str] = None
    quantity: int
    price: float
    total: float
    options: Optional[dict] = []
    serviceType: str

class CartFees(BaseModel):
    shipping: Optional[float] = 0.0
    tax: Optional[float] = 0.0
    handling: Optional[float] = 0.0
    voucherCode: Optional[str] = None
    voucherDiscount: Optional[float] = None

class CartProductSchema(BaseModel):
    type: Optional[str] = 'product'
    productId: str
    productName: str
    sellerName: str
    quantity: int
    price: float
    cartId: Optional[str] = None
    categoryId: str
    categoryName: Optional[str] = None
    image: Optional[str] = None
    slug: Optional[str] = None
    productType: str

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

# Response Model
def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": "OK"
    }

def ErrorResponseModel(code, message, status):
    return {
        "status": status,
        "code": code,
        "message": message,
    }

def ResponeSuccessMessage(message):
    return {
        "status": "OK",
        "code": 200,
        "message": message
    }
