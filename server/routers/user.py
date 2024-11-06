from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from server.models.user import (
    UserSchema,
)
from server.core.sendMailVerify import send_mail_verify
from server.crud.user import (
    crud_get_all_account,
    crud_post_add_account_data,
    crud_get_current_account
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Retrieve all acount
@router.get("/get-all", response_description="Account data from the database")
async def get_all_account():
   return await crud_get_all_account()

@router.post("/add", response_description="Account data added into the database")
async def add_account_data(account: UserSchema = Body(...)):
    return await crud_post_add_account_data(account)

@router.get("/get-user", response_description="Account data from the database")
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return await crud_get_current_account(request={"token": token})

@router.post("/send-mail", response_description="Send mail")
async def send_mail(user: UserSchema = Body(...)):
    resp = send_mail_verify(user)
    return resp
