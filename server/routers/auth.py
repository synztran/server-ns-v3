from datetime import datetime, timedelta
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
import motor.motor_asyncio
from server.database import generate_account_id, generate_customer_id
from typing import Optional
from uuid import uuid4

from server.models.schemas import Token, DataToken
from server.oauth2 import create_access_token, verify_password, hash_password
from server.models.user import CreateUserSchema, LoginUserSchema, ErrorResponseModel

import os
from dotenv import load_dotenv

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")

# TODO: We have RS256 and HS256 for decoding and encoding JWT
# HS256 using one secreat key for both encoding and decoding
# RS256 using public and private key for encoding and decoding

router = APIRouter()

# SECRET_KEY = '4a65948b27da9576fc0747702baaad98473359c92743367865faf8431c9812de'
SECRET_KEY = os.getenv("JWT_HEX32")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRES_IN = os.getenv("ACCESS_TOKEN_EXPIRES_IN")


# customer HTTPS exception
class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Optional[str] = None,
        message: str = None,
        status: str = None,
        errorCode: int = None,
    ):
        self.message = message
        self.status = status
        self.errorCode = errorCode
        super().__init__(status_code=status_code, detail={
            "message": message,
            "status": status,
            "errorCode": errorCode
        })

# create new user

@router.post('/register', status_code=status.HTTP_201_CREATED, response_description="Tài khoản đã được tạo thành công.")
async def create_user(payload: CreateUserSchema):
    # Check if user already exist
    user = await account_collection.find_one({"email": payload.email.lower()})
    if user:
        return ErrorResponseModel("", status.HTTP_409_CONFLICT, "Email đã tồn tại. Vui lòng thử lại.")
    # Hash the password
    payload.password = hash_password(payload.password)
    payload.accountId = await generate_account_id()
    payload.customerId = await generate_customer_id()
    payload.role = 'user'
    payload.verified = False
    payload.email = payload.email.lower()
    payload.createdAt = datetime.utcnow()
    payload.updatedAt = payload.createdAt
    payload.firstName = payload.firstName.title()
    payload.lastName = payload.lastName.title()
    payload.cartId = str(uuid4())
    payload.phoneNumber = payload.phoneNumber

    result = await account_collection.insert_one(payload.dict())
    if not result:
        return ErrorResponseModel("", status.HTTP_400_BAD_REQUEST, "Tạo tài khoản không thành công. Vui lòng thử lại.")
    return {"status": 'OK', "message": "Tài khoản đã được tạo thành công."}

# login user
@router.post('/login')
async def login(payload: LoginUserSchema) -> Token:
    # Check if user is exist
    db_user = await account_collection.find_one({'email': payload.email.lower()})
    if not db_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Không tìm thấy thông tin người dùng.",
                "status": status.HTTP_404_NOT_FOUND
            }
        )
    # Check if the pw is valid
    if not verify_password(payload.password, db_user['password']):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Tài khoản hoặc mật khẩu không đúng.",
                "status": status.HTTP_400_BAD_REQUEST
            }
        )

    # Create access token
    access_token_expires = timedelta(days=float(ACCESS_TOKEN_EXPIRES_IN))
    access_token = create_access_token(
        data={"sub": db_user["email"]}, expires_delta=access_token_expires
    )

    # Store refresh and access token in cookie
    # response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    # response.set_cookie('refresh_token', refresh_token,
    #                     REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    # response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
    #                     ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    
    # Send both access
    return Token(status='OK', data=[DataToken(bearerToken=access_token, tokenType="bearer", expiresIn=ACCESS_TOKEN_EXPIRES_IN)])
    # return {
    #     "status": "OK",
    #     "access_token": access_token,
    #     "token_type": "bearer"
    # }

# @router.get('/users/me/', response_model=User)
# async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
#     return current_user

# @router.get('/refresh')
# def refresh_token(response: Response, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_refresh_token_required()

#         user_id = Authorize.get_jwt_subject()
#         if not user_id:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not refresh access token")
        
#         user = userEntity(User.find_one({'_id': ObjectId(str(user_id))}))
#         if not user:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The user belonging to this token no logger exist')
        
#         access_token = Authorize.create_access_token(
#             subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
#     except Exception as e:
#         error = e.__class__.__name__
#         if error == 'MissingTokenError':
#              raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
#     response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
#                         ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
#     response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60,
#                         ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
#     return {'access_token': access_token}

# @router.get('/logout', status_code=status.HTTP_200_OK)
# def logout(response: Response, Authorize: AuthJWT = Depends(), user_id: str = Depends(oauth2.require_user)):
#     Authorize.unset_jwt_cookies()
#     response.set_cookie('logged_in', '', -1)

#     return {'status': 'success'}