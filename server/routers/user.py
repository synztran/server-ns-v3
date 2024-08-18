from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer
from server.oauth2 import decode_token, get_user
from typing import Annotated

from server.database import (
    # add_student,
    # delete_student,
    # retrieve_student,
    # retrieve_students,
    # update_student,
    retrieve_accounts,
    add_account
)
# from app.server.models.student import (
from server.models.user import (
    ErrorResponseModel,
    ResponseModel,
    UserSchema,
    # UpdateStudentModel,
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Retrieve all acount
@router.get("", response_description="Account data from the database")
async def get_all_account():
    accounts = await retrieve_accounts()
    if accounts:
        return ResponseModel(accounts, "Accounts data retrieve successfully")
    return ResponseModel(accounts, "Empty list returned")


@router.post("", response_description="Account data added into the database")
async def add_account_data(account: UserSchema = Body(...)):
    account = jsonable_encoder(account)
    new_account = await add_account(account)
    return ResponseModel(new_account, "Account added successfully.")

@router.get("/get_user", response_description="Account data from the database")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # Decode token
    payload = decode_token(token)
    if payload is None:
        return ErrorResponseModel("", 404, "User not found")
    
    # Retrieve user
    email = payload.email
    user_data = await get_user(email)
    print("user_data", user_data)

    if user_data is None:
        return ErrorResponseModel("", 404, "Không tìm thấy người dùng")
    
    formatRespUserData = {
        "email": user_data['email'],
        "firstName": user_data['firstName'],
        "lastName": user_data['lastName'],
        "phoneNumber": user_data['phoneNumber'],
        "shippingAt": user_data['shippingAt'],
        "verified": user_data['verified'],
        "phoneAreaCode": user_data['phoneAreaCode'],
        "createdAt":  user_data['createdAt'],
        "verifiedAt":   user_data['verifiedAt'],
        "getNoti": user_data['getNoti'] if 'getNoti' in user_data else False,
        "paypal":  user_data['paypal'],
        "fbUrl":  user_data['fbUrl'],
        "customerId": user_data['customerId'],
        "cartId": user_data['cartId'],
        "avatar": user_data['avatar'] if 'avatar' in user_data else "",
    }

    return ResponseModel(formatRespUserData, "Người dùng tìm thấy thành công")
