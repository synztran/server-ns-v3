from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from server.serializers.userSerializers import userEntity
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, Request
from server.models.schemas import TokenData
import motor.motor_asyncio

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

def hashPassword(password: str):
    return pwdContext.hash(password)

def verifyPassword(password: str, hashedPassword: str):
    check = hashPassword(password)
    return pwdContext.verify(password, hashedPassword)

async def getUser(email: str):
    currentUser = await accountCollection.find_one({"email": email})
    if currentUser:
        currentUser.pop("_id", None) # Remove the _id key
        return userEntity(currentUser)
    return None
    
def createAccessToken(data: dict, expiresDelta: timedelta):
    toEncode = data.copy()
    expire = datetime.utcnow() + expiresDelta
    toEncode.update({"exp": expire})
    encodedJwt = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodedJwt

def decodeToken(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Could not validate credentials")
        tokenData = TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return tokenData

def getBearerToken(req: Request) -> str:
    authorization: str = req.headers.get("Authorization")
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
    token = authorization[len("Bearer "):]
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return token

def userResponseEntity(user) -> dict:
    return {
        "customerId": user["customerId"],
        "accountId": user["accountId"],
        "email": user["email"],
        "firstName": user["firstName"],
        "lastName": user["lastName"],
        "dob": user["dob"],
        "createdAt": user["createdAt"],
        "updatedAt": user["updatedAt"],
        "role": user["role"],
        "verified": False,
        "getNoti": False,
        "cartId": user["cartId"],
    }