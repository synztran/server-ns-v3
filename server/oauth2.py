from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from server.serializers.userSerializers import userEntity, userResponseEntity
from datetime import datetime, timedelta
from jose import JWTError, jwt
# from server.config import settings
from fastapi import Depends, HTTPException, status, Request
from server.models.schemas import Token, TokenData, User
import motor.motor_asyncio

# fixed variable
# SECRET_KEY = settings.JWT_HEX32
# ALGORITHM = settings.JWT_ALGORITHM
# ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
SECRET_KEY = '4a65948b27da9576fc0747702baaad98473359c92743367865faf8431c9812de'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_IN = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# access db
MONGO_DETAILS = "mongodb+srv://admin:123456Ban@cluster0.u7ysm.mongodb.net/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str):
    check = hash_password(password)
    return pwd_context.verify(password, hashed_password)

async def get_user(email: str):
    currentUser = await account_collection.find_one({"email": email})
    if currentUser:
        currentUser.pop("_id", None) # Remove the _id key
        return userEntity(currentUser)
    
    return None
    
def authenticate_user(fake_db, email: str, password: str):
    user = get_user(fake_db, email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Could not validate credentials")
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return token_data

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