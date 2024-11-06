from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

from server.models.cart import CartFees, CartProductSchema, CartService, CartProductSchema

class EnumOrderStatus(Enum):
    ORDERED = 'ORDERED'
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'

class EnumOrderPaymentStatus(Enum):
    PAID = 'PAID'
    PENDING = 'PENDING'
    CANCLELLED = 'CANCELLED'

class Customer(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    address: str

class OrderInfo(BaseModel):
    country: str
    firstName: str
    lastName: str
    company: Optional[str] = ''
    address: str
    apartment: Optional[str] = ''
    city: str
    province: str
    postCode: str
    phoneNumber: str
    deliveryMethod: str
    paymentMethod: str
    billingAddress: Optional[str | dict] = None
    note: Optional[str] = ''

class ServiceItem(BaseModel):
    name: str
    description: str
    price: float

class OrderSchema(BaseModel):
    services: List[CartService] = []
    products: List[CartProductSchema] = []
    orderedAt: Optional[str] = ''
    fees: Optional[CartFees] = {}
    orderInfo: OrderInfo
    cartId: str
    customerId: int
    totalPrice: float
    paymentStatus: Optional[EnumOrderPaymentStatus] = 'PENDING'
    orderStatus: Optional[EnumOrderStatus] = 'PENDING'
    totalQuantity: Optional[int] = 0


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": 'OK'
    }

def ErrorResponseModel(error, code, message):
    return {
        "error": error,
        "code": code,
        "message": message,
        "status": "ERROR"
    }
