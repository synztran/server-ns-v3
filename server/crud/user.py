import motor.motor_asyncio
import os
from dotenv import load_dotenv
from uuid import uuid4
from server.core.generate import generate_account_id, generate_customer_id
from server.core.database import account_helper
from server.models.user import ResponseModel, ErrorResponseModel
from fastapi.encoders import jsonable_encoder
from server.core.oauth2 import decode_token, get_user

# connect db from .env file
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")

# functions
async def retrieve_accounts():
    accounts = []
    async for account in account_collection.find():
        accounts.append(account_helper(account))
    return accounts
async def add_account(account_data: dict) -> dict:
    account_id = await generate_account_id()
    customer_id = await generate_customer_id()
    account_data["accountId"] = account_id
    account_data["customerId"] = customer_id
    account_data["cartId"] = str(uuid4())
    account = await account_collection.insert_one(account_data)
    new_account = await account_collection.find_one({"_id": account.inserted_id})
    return account_helper(new_account)

async def crud_get_all_account():
    accounts = await retrieve_accounts()
    if accounts:
        return ResponseModel(accounts, "Accounts data retrieve successfully")
    return ResponseModel(accounts, "Empty list returned")
async def crud_post_add_account_data(request: dict):
    account = jsonable_encoder(account)
    new_account = await add_account(account)
    return ResponseModel(new_account, "Account added successfully.")
async def crud_get_current_account(request: dict):
    decode_data = decode_token(request['token'])
    if decode_data is None:
        return ErrorResponseModel("", 404, "User not found")
    email = decode_data.email
    user_data = await get_user(email)
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
        "accountId": user_data['accountId'],
    }
    return ResponseModel(formatRespUserData, "Account data retrieve successfully")
