import motor.motor_asyncio
import pymongo
import os

from dotenv import load_dotenv
from uuid import uuid4
from server.core.generate import generateAccountId, generateCustomerId, accountHelper


# connect db from .env file
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")

# model
# User = database.users
# User.create_index([("email"), pymongo.ASCENDING], unique=True)

# User's Functions
async def getAllAccount():
    accounts = []
    async for account in account_collection.find():
        accounts.append(accountHelper(account))
    return accounts

async def addNewAccount(account_data: dict) -> dict:
    accountId = await generateAccountId()
    customerId = await generateCustomerId()
    account_data["accountId"] = accountId
    account_data["customerId"] = customerId
    account_data["cartId"] = str(uuid4())
    account = await account_collection.insert_one(account_data)
    new_account = await account_collection.find_one({"_id": account.inserted_id})
    return accountHelper(new_account)
