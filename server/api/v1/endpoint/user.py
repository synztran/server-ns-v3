from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer

# from server.crud.user import getAllAccount, addNewAccount
# from server.models.user import ErrorResponseModel, ResponseModel, UserSchema
# from server.core.oauth2 import decodeToken, getUser

# Authen
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")

router = APIRouter()

# @router.post("", response_description="Account data added into the database")
# async def createUser(data: UserSchema = Body(...)):
#     accountData = jsonable_encoder(data)
#     newAccount = await addNewAccount(accountData)
#     if not newAccount:
#         return ErrorResponseModel("An error occurred", 404, "Account not added")
#     return ResponseModel(newAccount, "Account added successfully.")

# @router.get("", response_description="Account data from the database")
# async def readAllUser():
#     users = await getAllAccount()
#     if users:
#         return ResponseModel(users, "Users data retrieve successfully")
#     return ResponseModel(users, "Empty list returned")

# @router.get("/get_user", response_description="Account data from the database")
# async def readUser(token:  Annotated[str,Depends(oauth2Scheme)]):
#     # Decode token
#     payload = decodeToken(token)
#     if payload is None:
#         return ErrorResponseModel("", 404, "User not found")

#     # Retrieve user
#     email = payload.email
#     user_data = await getUser(email)

#     if user_data is None:
#         return ErrorResponseModel("", 404, "Không tìm thấy người dùng")

#     formatRespUserData = {
#         "email": user_data['email'],
#         "customerId": user_data['customerId'],
#         "accountId": user_data['accountId'],
#         "cartId": user_data['cartId']
#     }
#     return ResponseModel(formatRespUserData, "User data retrieved successfully")
