from bson import ObjectId
import motor.motor_asyncio

from fastapi import HTTPException
from typing import List, Optional, Union

from server.models.order import OrderSchema, EnumOrderStatus, EnumOrderPaymentStatus
from server.models.category import ParamsGet, StatusGB
from datetime import datetime
from uuid import uuid4

import logging

MONGO_DETAILS = "mongodb+srv://admin:123456Ban@cluster0.u7ysm.mongodb.net/"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)


database = client.testmongodb

account_collection = database.get_collection("accounts")
category_collection = database.get_collection("categories")
product_collection = database.get_collection("products")
product_option_collection = database.get_collection("productOptions")
order_collection = database.get_collection("orders")

# User = database.users
# User.create_index([("email"), pymongo.ASCENDING], unique=True)

# utils
async def generate_id(collection: str):
    switcher = {
        "account": {
            "collection": account_collection,
            "field": "customerId",
        },
        "category": {
            "collection": category_collection,
            "field": "categoryId"
        },
        "product": {
            "collection": product_collection,
            "field": "productId"
        },
    }

    generate_collection = switcher.get(collection, "nothing").collection
    generate_field = switcher.get(collection, "nothing").field

    max_id = await generate_collection.find_one(sort=[generate_field, -1])

    if max_id:
        return max_id[generate_field] + 1
    else:
        return 1
    
async def generate_orderId(services: List, products: List) -> str:
    # Determine XX base on services and products
    if services and products:
        XX = "02"
    else:
        XX = "01"

    # get the current date
    current_date = datetime.now().strftime("%d%m%y")
    orders = order_collection.find({})
    documentOrders = await orders.to_list(length=100000)
    newOrderId = int(len(documentOrders) + 1) if len(documentOrders) > 0 else 1
    formattedOrderId = f"ORDER-{current_date}{XX}-{str(newOrderId).zfill(4)}"
    return formattedOrderId

# account
async def generate_customer_id():
    # Find the maximum customer_id from existing documents
    maxCustomerId = await account_collection.find_one(sort=[("customerId", -1)])
    if maxCustomerId:
        return maxCustomerId["customerId"] + 1
    else:
        # no existing documents, start from 1
        return 1

async def generate_account_id():
    # Find the maximum account_id from existing documents
    maxAccountId = await account_collection.find_one(sort=[("accountId", -1)])
    if maxAccountId:
        return maxAccountId["accountId"] + 1
    else:
        # No existing documents, start from 1
        return 1


def account_helper(account) -> dict:
    # Can't using async on this func => make Internal Server
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
        "verified": account["verified"] if "verified" in account else False,
        "phoneAreaCode": account["phoneAreaCode"] if "phoneAreaCode" in account else "",
        "createdAt":  account["createdAt"],
        "getNoti": account["getNoti"] if "getNoti" in account else False,
        "paypal":  account["paypal"] if "paypal" in account else "",
        "fbUrl":  account["fbUrl"] if "fbUrl" in account else "",
        "cartId":  account["cartId"] if "cartId" in account else "",
        "updatedAt": account["updatedAt"],
        "customerId": account["customerId"],
        "accountId": account["accountId"],
        "verifiedAt": formatActiveDate if "verifiedAt" in account else "",
    }

# Retrieve all accounts present in the database
async def retrieve_accounts():
    accounts = []
    async for account in account_collection.find():
        accounts.append(account_helper(account))
    return accounts

# Add a new student into to the database
async def add_account(account_data: dict) -> dict:
    accountId = await generate_account_id()
    customerId = await generate_customer_id()
    account_data["accountId"] = accountId
    account_data["customerId"] = customerId
    account_data["cartId"] = str(uuid4())
    account = await account_collection.insert_one(account_data)
    new_account = await account_collection.find_one({"_id": account.inserted_id})
    return account_helper(new_account)


# category
def category_helper(category) -> dict:
    return {
        "category_id": category["category_id"],
        "slug": category["slug"],
        "category_name": category["category_name"],
        "manufacturing": category["manufacturing"],
        "author": category["author"],
        "proxy_host": category["proxy_host"],
        "status_gb": category["status_gb"],
        "type": category["type"],
        "date_start": category["date_start"],
        "date_end": category["date_end"],
        "date_payment": category["date_payment"],
        "min_price": category["min_price"],
        "max_price": category["max_price"],
        "tax": category["tax"],
        "handle": category["handle"],
        "pic_profile": {
            "path": category["pic_profile"].get("path", ""), 
            "size": category["pic_profile"].get("size", 0)
        }        ,
        "get_noti": category.get("get_noti", False),
        "time_line": category.get("time_line", {}),
        "is_active": category.get("is_active", False),
        "description": category.get("description", ""),
        "pic_list": category.get("pic_list", []),
        "collapse_content": category.get("collapse_content", []),
        "sale_price": category.get("sale_price", 0),
        "is_active": category.get("is_active", False),
    }


async def retrieveCategoriesByParams(params: ParamsGet):
    status_gb = params.status_gb if params.status_gb else ""
    slug = params.slug if params.slug else ""
    ids = params.ids if params.ids else []
    categories = []
    if status_gb != "":
        async for category in category_collection.find({
            "status_gb": {"$eq": status_gb}
        }):
            categories.append(category_helper(category))
        return categories
    if slug != "":
        async for category in category_collection.find({
            "slug": {"$eq": slug}
        }):
            categories.append(category_helper(category))
        return categories
    if len(ids) > 0:
        async for category in category_collection.find({
            "category_id": {"$in": ids}
        }):
            categories.append(category_helper(category))
        return categories
    else:
        async for category in category_collection.find():
            categories.append(category_helper(category))
        return categories
    
async def retrieveCategories(status_gb: str, slug: str):
    categories = []
    if status_gb != "":
        async for category in category_collection.find({
            "status_gb": {"$eq": status_gb}
        }):
            categories.append(category_helper(category))
        return categories
    if slug != "":
        async for category in category_collection.find({
            "slug": {"$eq": slug}
        }):
            categories.append(category_helper(category))
        return categories
    else:
        async for category in category_collection.find():
            categories.append(category_helper(category))
        return categories


async def add_category(category_data: dict) -> dict:
    category_id = await generate_id("category")
    category_data["category_id"] = category_id
    category = await category_collection.insert_one(category_data)
    new_category = await category_collection.find_one({"_id": category.inserted_id})
    return category_helper(new_category)


async def retrieve_category_by_id(slug: str):
    category = await category_collection.find_one({"slug": slug})

    if category:
        return category_helper(category)

    raise HTTPException(status_code=404, detail=f"Category with ID {slug} not found")


# product
def product_helper(product) -> dict:
    # Can't using async on this func => make Internal Server

    return {
        "product_id": product["product_id"],
        "product_name": product["product_name"],
        "replace_product_name": product["replace_product_name"],
        "category_id": product["category_id"],
        "slug": product["slug"] if "slug" in product else "",
        "product_part": product["product_part"],
        "outstock": product["outstock"],
        "price": product["price"],
        "pic_product": product["pic_product"],
        "pic_list": product.get("pic_list", []),
        "quantity": product["quantity"] if "quantity" in product else 0,
    }

async def retrieve_products():
    products = []
    async for product in product_collection.find():
        products.append(product_helper(product))
    return products

async def add_product(product_data: dict) -> dict:
    product_id = await generate_id("product")
    product_data["product_id"] = product_id
    product = await product_collection.insert_one(product_data)
    new_product = await product_collection.find_one({"_id": product.inserted_id})
    return product_helper(new_product)

async def retrieve_product_by_id(product_id):
    product = await product_collection.find_one({"product_id": product_id})

    if product:
        return product_helper(product)
    
    raise HTTPException(status_code=404, detail=f"Product with ID {product_id} not found")

async def retrieve_products_by_id(category_id):
    products = []
    # products = await product_collection.find({"category_id": category_id})
    async for product in product_collection.find({"category_id": category_id}):
        products.append(product_helper(product))

    if products:
        return products
    
    raise HTTPException(status_code=404, detail=f"All Product with ID {category_id} not found")
# collection

# product opt
def product_option_helper(product_option) -> dict:
    # Can't using async on this func => make Internal Server

    return {
        "productOptionID": product_option["productOptionID"],
        "productId": product_option["productId"],
        "productOptionName": product_option["productOptionName"],
        "productOptionPrice": product_option["productOptionPrice"],
        "imageUrl": product_option["imageUrl"],
        "status": product_option["status"],
        "quanlity": product_option["quanlity"],
    }


async def retrieve_product_opts(product_id):
    productOpts = []

    # Assuming 'product_id' is the field in the collection
    query = {"product_id": product_id}
    projection = {"_id": 0}  # Exclude _id

    #     productOpts.append(opt)
    async for opt in product_option_collection.find(query, projection):
        productOpts.append(opt)

    if productOpts:
        return productOpts
        
    # raise HTTPException(status_code=404, detail=f"All Product with ID {product_id} not found")
    return []

async def retrieveProductByParams(params: ParamsGet):
    ids = params.ids if params.ids else []
    products = []
    if len(ids) > 0:
        async for product in product_collection.find({
            "product_id": {"$in": ids}
        }):
            products.append(product_helper(product))
        return products
    else:
        async for product in product_collection.find():
            products.append(product_helper(product))
        return products

# order

def orderHelper(order) -> dict:
    return {
        "orderId": order["orderId"],
        "customerId": order["customerId"],
        "services": order["services"],
        "products": order["products"],
        "totalPrice": order["totalPrice"],
        "orderedAt": order["orderedAt"],
        "fees": order["fees"],
        "cartId": order["cartId"],
        "orderInfo": order["orderInfo"],
    }

async def create_order(orderData: dict) -> Union[dict, None]:
    try:
        print("orderData: ", orderData)
        orderId = await generate_orderId(orderData["services"], orderData["products"])
        orderData["orderId"] = orderId
        orderData["totalPrice"] = orderData["totalPrice"]
        orderData['orderedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orderTotalQuantity = sum(product["quantity"] for product in orderData['products'])
        print("orderTotalQuantity", orderTotalQuantity)
        orderData['totalQuantity'] = orderTotalQuantity if orderTotalQuantity > 0 else 0
        orderData['paymentStatus'] = EnumOrderPaymentStatus.PENDING.value
        orderData['orderStatus'] = EnumOrderStatus.ORDERED.value
        
        order = await order_collection.insert_one(orderData)
        newOrder = await order_collection.find_one({"_id": order.inserted_id})
        if newOrder:
            cart = await account_collection.find_one({"cartId": orderData["cartId"]})
            if cart:
                # clear cart data when new order is created
                await account_collection.update_one(
                    {"cartId": orderData["cartId"]}, 
                    {"$set": {
                        "cartId": str(uuid4()),
                        "products": [],
                        "services": [],
                        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "totalPrice": 0,
                        "fees": {
                            "shipping": 0,
                            "tax": 0,
                            "handling": 0,
                            "voucherCode": "",
                            "voucherDiscount": 0
                        }
                    }}
                )
        else:
            return None
        return orderHelper(newOrder)
    except Exception as e:
        print("Error: ", e)
        return False

async def update_order(orderId: str, new_data: dict):
    # Return false if an empty request body is sent.
    if len(new_data) < 1:
        return False
    order = await order_collection.find_one({"orderId": orderId})
    if order:
        updated_order = await order_collection.update_one(
            {"orderId": orderId}, {"$set": new_data}
        )
        if updated_order:
            return True
        return False
    
async def retrieveOrder(orderId: str):
    order = await order_collection.find_one({"orderId": orderId})
    if order:
        return orderHelper(order)
    return None