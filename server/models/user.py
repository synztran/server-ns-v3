from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr

from datetime import datetime, timezone


class ShippingAt(BaseModel):
    firstName: str
    lastName: str
    companyName: str
    email: EmailStr
    townCity: str
    phoneNumber: str
    address: str
    country: str
    zipCode: int

class UserSchema(BaseModel):
    customerId: int = Field(...)
    accountId: int = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    firstName: str = Field(...)
    lastName: str = Field(...)
    dob: str = Field(...)
    shippingAt: ShippingAt
    phoneAreaCode: str
    phoneNumber: str
    createdAt: datetime | None = None
    updatedAt: datetime | None = None
    verifiedAt: datetime | None = None
    getNoti: bool = False
    paypal: str
    fbUrl: str
    registrationToken: str
    expirationTokenAt: datetime
    role: str | None = None
    verified: bool = False
    cartId: str
    avatar: str | None = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "email": "abc@gmail.com",
                "password": "123456abc",
                "firstName": "Hari",
                "lastName": "Chan",
                "dob": "01/01/2001",
                "shippingAt": {
                    "firstName": "A",
                    "lastName": "Giang",
                    "cname": "Long",
                    "email": "a.giang@gmail.com",
                    "townCity": "Ho chi minh",
                    "phoneNumber": "+84 123456789",
                    "address": "53 barker street, Berminham, London",
                    "country": "England",
                    "zip_code": '35000'
                },
                "phoneAreaCode": "+84",
                "phoneNumber": "+84 123456789",
                "created": "",
                "active": False,
                "active_date":  None,
                "getNoti": False,
                "paypa": "",
                "fbUrl": "",
                "registrationToken": "",
                "expirationTokenAt": "",
                "cartId": ""
            }
        }

class CreateUserSchema(BaseModel):
    accountId: int = None
    customerId: int = None
    role: str = 'user'
    firstName: str
    lastName: str
    email: str
    createdAt: datetime = None
    updatedAt: datetime = None
    password: str
    verified: bool = False
    cartId: str = ""
    phoneNumber: str

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=6) # type: ignore

class UserResponseSchema(UserSchema):
    id: str
    pass

class AccountResponse(BaseModel):
    user: UserResponseSchema

class VerifyMailSchema(BaseModel):
    token: str

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
        "status": "OK"
    }

def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
