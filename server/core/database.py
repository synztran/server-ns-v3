import motor.motor_asyncio
from typing import List

# connect to MongoDB
MONGO_DETAILS = "mongodb+srv://admin:123456Ban@cluster0.u7ysm.mongodb.net/"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
account_collection = database.get_collection("accounts")
category_collection = database.get_collection("categories")
product_collection = database.get_collection("products")
product_option_collection = database.get_collection("productOptions")
order_collection = database.get_collection("orders")

# def
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

# category
def category_helper(category) -> dict:
    return {
        "categoryId": category["categoryId"] if "categoryId" in category else "",
        "slug": category["slug"] if "slug" in "slug" in category else "",
        "categoryName": category["categoryName"] if "categoryName" in category else "",
        "manufacturing": category["manufacturing"] if "manufacturing" in category else "",
        "author": category["author"],
        "proxyHost": category["proxyHost"],
        "statusGb": category["statusGb"],
        "type": category["type"],
        "dateStart": category["dateStart"],
        "dateEnd": category["dateEnd"],
        "datePayment": category["datePayment"],
        "minPrice": category["minPrice"],
        "maxPrice": category["maxPrice"],
        "tax": category["tax"],
        "handle": category["handle"],
        "picProfile": {
            "path": category["picProfile"].get("path", ""),
            "size": category["picProfile"].get("size", 0)
        }        ,
        "getNoti": category.get("getNoti", False),
        "timeLine": category.get("timeLine", {}),
        "isActive": category.get("isActive", False),
        "description": category.get("description", ""),
        "picList": category.get("picList", []),
        "collapseContent": category.get("collapseContent", []),
        "salePrice": category.get("salePrice", 0),
    }

# product
def product_helper(product) -> dict:
    # Can't using async on this func => make Internal Server
    return {
        "productId": product["productId"],
        "productName": product["productName"],
        "replaceProductName": product["replaceProductName"],
        "categoryId": product["categoryId"],
        "slug": product["slug"] if "slug" in product else "",
        "productPart": product["productPart"],
        "outstock": product["outstock"],
        "price": product["price"],
        "picProduct": product["picProduct"],
        "picList": product.get("picList", []),
        "quantity": product["quantity"] if "quantity" in product else 0,
        "weight": product["weight"] if "weight" in product else 0,
    }

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

# order re-map data
def order_helper(order) -> dict:
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

def fix_object_id(document):
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document

def config_helper(config) -> List[dict]:
    return [{
        "shippingRate": config["shippingRate"],
    }]
