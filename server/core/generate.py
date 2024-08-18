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
accountCollection = database.get_collection("account_collection")
categoryCollection = database.get_collection("categories")
productCollection = database.get_collection("products")
productOptionCollection = database.get_collection("productOptions")
orderCollection = database.get_collection("orders")


# generate id
async def generateId(collection: str):
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
    
async def generateOrderId(services: List, products: List) -> dict:
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
    
async def generateCustomerId():
    # Find the maximum customer_id from existing documents
    maxCustomerId = await accountCollection.find_one(sort=[("customerId", -1)])
    if maxCustomerId:
        return maxCustomerId["customerId"] + 1
    else:
        return 1 
    
async def generateAccountId():
    # Find the maximum account_id from existing documents
    maxAcccountId = await accountCollection.find_one(sort=[("accountId", -1)])
    if maxAcccountId:
        return maxAcccountId["account_id"] + 1
    else:
        return 1

# helper
    # Can't using async on this func => make Internal Server

def accountHelper(account) -> dict:
    if "verifiedAt" in account:
        # Check if the value of "active_date" is a string
        if isinstance(account["verifiedAt"], str):
            formatActiveDate = account["verifiedAt"]
        else:
            formatActiveDate = ""
    else:
        formatActiveDate = ""

    return {
        "firstName": account["firstName"],
        "lastName": account["lastName"],
        "email": account["email"],
        "shippingAt": account["shippingAt"][0] if "shippingAt" in account else [],
        "phoneNumber": account["phoneNumber"] if "phoneNumber" in account else "",
        "phoneAreaCode": account["phoneAreaCode"] if "phoneAreaCode" in account else "",
        "createdAt":  account["createdAt"] if "createdAt" in account else "",
        "verified":   account["verified"] if "verified" in account else False,
        "verifiedAt":  formatActiveDate,
        "updatedAt": account["updatedAt"] if "updatedAt" in account else "",
        "getNoti": account["getNoti"] if "getNoti" in account else False,
        "paypal":  account["paypal"] if "paypal" in account else "",
        "fbUrl":  account["fbUrl"] if "fbUrl" in account else "",
        "cartId":  account["cartId"] if "cartId" in account else "",
    }

def categoryHelper(category) -> dict:
    return {
        "categoryId": category["category_id"],
        "slug": category["slug"],
        "categoryName": category["category_name"],
        "manufacturing": category["manufacturing"],
        "author": category["author"],
        "proxyHost": category["proxy_host"],
        "status": category["status_gb"],
        "type": category["type"],
        "dateStart": category["date_start"],
        "dateEnd": category["date_end"],
        "datePayment": category["date_payment"],
        "minPrice": category["min_price"],
        "maxPrice": category["max_price"],
        "tax": category["tax"],
        "handle": category["handle"],
        "picProfile": {
            "path": category["pic_profile"].get("path", ""), 
            "size": category["pic_profile"].get("size", 0)
        }        ,
        "timeLine": category.get("time_line", {}),
        "isActive": category.get("is_active", False),
        "description": category.get("description", ""),
        "picList": category.get("pic_list", []),
        "collapseContent": category.get("collapse_content", []),
        "salePrice": category.get("sale_price", 0),
        "isActive": category.get("is_active", False),
    }

def product_helper(product) -> dict:
    return {
        "productId": product["product_id"],
        "productName": product["product_name"],
        "replaceProductName": product["replace_product_name"],
        "categoryId": product["category_id"],
        "slug": product["slug"],
        "productPart": product["product_part"],
        "outstock": product["outstock"],
        "price": product["price"],
        "picProduct": product["pic_product"],
        "picList": product.get("pic_list", []),
        "quantity": product["quantity"] if "quantity" in product else 0,
    }

def productOptionHelper(product_option) -> dict:
    return {
        "productOptionID": product_option["productOptionID"],
        "productId": product_option["product_id"],
        "productOptionName": product_option["productOptionName"],
        "productOptionPrice": product_option["productOptionPrice"],
        "imageUrl": product_option["imageUrl"],
        "status": product_option["status"],
        "quanlity": product_option["quanlity"],
    }

def orderHelper(order) -> dict:
    return {
        "orderId": order["orderId"],
        "customerId": order["customerId"],
        "services": order["services"],
        "products": order["products"],
        "totalAmount": order["totalAmount"],
        "orderedAt": order["orderedAt"],
    }