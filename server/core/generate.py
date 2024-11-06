import motor.motor_asyncio
import pymongo
import os

from fastapi import HTTPException
from typing import List, Optional
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4


# connect db from .env file
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
accountCollection = database.get_collection("accounts")
categoryCollection = database.get_collection("categories")
productCollection = database.get_collection("products")
productOptionCollection = database.get_collection("productOptions")
orderCollection = database.get_collection("orders")


# generate id
async def generate_id(collection: str):
    switcher = {
        "account": {
            "collection": accountCollection,
            "field": "customerId",
        },
        "category": {
            "collection": categoryCollection,
            "field": "categoryId"
        },
        "product": {
            "collection": productCollection,
            "field": "productId"
        },
    }

    generateCollection = switcher.get(collection, "nothing").collection
    generateField = switcher.get(collection, "nothing").field

    max_id = await generateCollection.find_one(sort=[generateField, -1])

    if max_id:
        return max_id[generateField] + 1
    else:
        return 1

async def generate_order_id(services: List, products: List) -> dict:
    # get the current date
    currentDate = datetime.now().strftime("%d%m%y")

    # Determine XX base on services and products
    if services and products:
        XX = "02"
    else:
        XX = "01"

    maxOrderId = await orderCollection.find_one(sort=[("orderId", -1)])
    if maxOrderId:
        return f"{currentDate}{XX}-{maxOrderId['orderId'] + 1}"
    else:
        return f"{currentDate}{XX}-0001"

async def generate_customer_id():
    # Find the maximum customer_id from existing documents
    maxCustomerId = await accountCollection.find_one(sort=[("customerId", -1)])
    if maxCustomerId:
        return maxCustomerId["customerId"] + 1
    else:
        return 1

async def generate_account_id():
    # Find the maximum account_id from existing documents
    maxAcccountId = await accountCollection.find_one(sort=[("accountId", -1)])
    if maxAcccountId:
        return maxAcccountId["accountId"] + 1
    else:
        return 1

def generate_cart_id():
    return str(uuid4())
