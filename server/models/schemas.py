from datetime import datetime
from typing import List
from pydantic import BaseModel, EmailStr, constr

class DataToken(BaseModel):
    bearerToken: str
    tokenType: str
    expiresIn: int

class Token(BaseModel):
    status: str
    # access_token: str
    # token_type: str
    data: List[DataToken]


class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None

class User(BaseModel):
    name: str
    email: str
    photo: str
    role: str | None = None
    createdAt: datetime | None = None
    updatedAt: datetime | None = None

    class Config:
        from_attributes = True

class UserInDB(User):
    password: str


class CreateUserSchema(User):
    customerId: int
    accountId: int
    firstName: str
    lastName: str
    email: str
    password: str
    passwordConfirm: str
    verified: bool = False

class LoginUserSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(User):
    id: str
    pass

class UserResponse(BaseModel):
    status: str
    user: UserResponseSchema

def ErrorResponseModel(code, message):
    return {
        "code": code,
        "message": message
    }
