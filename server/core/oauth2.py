from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from server.core.userSerializers import user_entity
from datetime import datetime, timedelta
from jose import JWTError
import jwt
from fastapi import Request, status
from server.models.schemas import TokenData
import motor.motor_asyncio
from server.core.utils import CustomHTTPException
from server.models.user import VerifyMailSchema
from jwt import PyJWTError

import os
from dotenv import load_dotenv

# get secret key from .env
load_dotenv()
SECRET_KEY = os.environ.get('JWT_HEX32')
ALGORITHM = os.environ.get('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRES_IN = os.environ.get('ACCESS_TOKEN_EXPIRES_IN')

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="token")

# access db
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
accountCollection = database.get_collection("accounts")

# utils

def hash_password(password: str):
    return pwdContext.hash(password)

def verify_password(password: str, hashedPassword: str):
    # check = hash_password(password)
    return pwdContext.verify(password, hashedPassword)

async def get_user(email: str):
    currentUser = await accountCollection.find_one({"email": email})
    if currentUser:
        currentUser.pop("_id", None) # Remove the _id key
        return user_entity(currentUser)
    return None

def create_access_token(data: dict, expires_delta: timedelta):
    toEncode = data.copy()
    expire = datetime.utcnow() + expires_delta
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        print("email email", email)
        if email is None:
            raise CustomHTTPException(code=status.HTTP_403_FORBIDDEN, message="Could not validate credentials", status="Error")
        tokenData = TokenData(email=email)
    except JWTError:
        raise CustomHTTPException(code=status.HTTP_403_FORBIDDEN, message="Could not validate credentials", status="Error")
    return tokenData

def get_bearer_token(req: Request) -> str:
    authorization: str = req.headers.get("Authorization")
    if authorization is None or not authorization.startswith("Bearer "):
        raise CustomHTTPException(code=status.HTTP_401_UNAUTHORIZED, message="Invalid or missing Authorization header", status="Error")

    token = authorization[len("Bearer "):]
    if not token:
        raise CustomHTTPException(code=status.HTTP_401_UNAUTHORIZED, message="Invalid token", status="Error")

    return token

def get_auth_user(req: Request):
    token = get_bearer_token(req)
    tokenData = decode_token(token)
    if tokenData is None:
        return None
    return tokenData


def create_verification_token(accountId: int):
    expiration = datetime.utcnow() + timedelta(hours=24)
    payload = {
        "sub": accountId,
        "exp": expiration
    }
    print("ALGORITHM", ALGORITHM)
    encodedJwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print("encodedJwt encodedJwt", encodedJwt)
    return encodedJwt

def mail_verify_token(request: VerifyMailSchema):
    try:
        token = request.token
        print("token", token)
        print("SECRET_KEY", SECRET_KEY)
        payload_decode = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("payload_decode", payload_decode)
        account_id: int = payload_decode.get("sub")
        print("account_id", account_id)
        valid_account_id = accountCollection.find_one({"accountId": account_id}, {"_id": 0, "accountId": 1})
        print("valid_account_id", valid_account_id)
        # check valid account id
        if valid_account_id is None:
            raise CustomHTTPException(code=status.HTTP_403_FORBIDDEN, message="Could not validate credentials", status="Error")
        # if valid update verified field
        accountCollection.update_one({"accountId": account_id}, {"$set": {"verified": True}})
    except PyJWTError:
        raise CustomHTTPException(code=status.HTTP_403_FORBIDDEN, message="Could not validate credentials", status="Error")
    raise CustomHTTPException(code=status.HTTP_200_OK, message="Tài khoản đã được xác thực.", status="OK")
