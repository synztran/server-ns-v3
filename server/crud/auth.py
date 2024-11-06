from server.models.user import CreateUserSchema, LoginUserSchema, ErrorResponseModel
from fastapi import status
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

from server.core.oauth2 import hash_password
from server.core.generate import generate_account_id, generate_customer_id
from server.models.schemas import Token, DataToken
from server.core.oauth2 import create_access_token, verify_password, hash_password
from server.core.utils import CustomHTTPException, CustomJSONResponse
from server.core.sendMailVerify import send_mail_verify

import os
import motor.motor_asyncio

# TODO: We have RS256 and HS256 for decoding and encoding JWT
# TODO: HS256 using one secreat key for both encoding and decoding
# TODO: RS256 using public and private key for encoding and decoding

# static file
SECRET_KEY = os.getenv("JWT_HEX32")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRES_IN = os.getenv("ACCESS_TOKEN_EXPIRES_IN")

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")

# crud def
async def crud_create_user(request: CreateUserSchema):
  req_email = request.email.lower()
  user = await account_collection.find_one({"email": req_email})
  if user:
      raise CustomHTTPException(
        code=status.HTTP_409_CONFLICT,
        status="Error",
        message="Email đã tồn tại. Vui lòng thử lại."
      )

  # format request
  request.password = hash_password(request.password)
  request.accountId = await generate_account_id()
  request.customerId = await generate_customer_id()
  request.role = 'user'
  request.verified = False
  request.email = request.email.lower()
  request.createdAt = datetime.now(timezone.utc)
  request.updatedAt = request.createdAt
  request.firstName = request.firstName.title()
  request.lastName = request.lastName.title()
  request.cartId = str(uuid4())
  request.phoneNumber = request.phoneNumber

  # send mail verify
  # TODO: Need send to log when send mail failed
  resp_send_mail_verify = send_mail_verify(request.dict(), request.accountId)
  if resp_send_mail_verify.get("status") == "Error":
      raise CustomHTTPException(
        code=status.HTTP_400_BAD_REQUEST,
        status="Error",
        message="Gửi mail xác thực không thành công. Vui lòng thử lại."
      )

  result = account_collection.insert_one(request.dict())
  if not result:
      raise CustomHTTPException(
        code=status.HTTP_400_BAD_REQUEST,
        status="Error",
        message="Tạo tài khoản không thành công. Vui lòng thử lại."
      )
  raise CustomHTTPException(
      code=status.HTTP_201_CREATED,
      message="Tài khoản đã được tạo thành công.",
      status="OK"
  )

async def crud_login_user(request: LoginUserSchema) -> Token:
    req_email = request.email.lower()
    req_password = request.password
    result_user = await account_collection.find_one({'email': req_email})
    if not result_user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message": "Không tìm thấy thông tin người dùng.",
                "status": status.HTTP_404_NOT_FOUND
            }
        )
    if not verify_password(req_password, result_user['password']):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": "Tài khoản hoặc mật khẩu không đúng.",
                "status": status.HTTP_400_BAD_REQUEST
            }
        )
    access_token_expires = timedelta(days=float(ACCESS_TOKEN_EXPIRES_IN))
    access_token = create_access_token(
        data={"sub": result_user["email"]}, expires_delta=access_token_expires
    )
    return Token(
        status='OK',
        data=[DataToken(bearerToken=access_token, tokenType="bearer", expiresIn=ACCESS_TOKEN_EXPIRES_IN)])
