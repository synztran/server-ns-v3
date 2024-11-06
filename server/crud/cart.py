import os
from dotenv import load_dotenv
import motor.motor_asyncio
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from server.core.oauth2 import get_bearer_token
from server.routers.user import get_current_user
from server.models.cart import CartProductSchema, ErrorResponseModel, ResponseModel, ResponeSuccessMessage, RemoveCartItemSchema, UpdateCartProduct, CartSchema
from datetime import datetime
from server.core.generate import generate_cart_id
import logging
from fastapi.responses import JSONResponse
from server.core.utils import CustomJSONResponse, CustomHTTPException

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
cart_collection = database.get_collection("carts")
category_collection = database.get_collection("categories")
product_collection = database.get_collection("products")
account_collection = database.get_collection("accounts")

# functions
def fix_object_id(document):
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document

#crud
async def crud_create_cart(request: dict):
    cart = jsonable_encoder(request)
    newCart = await cart_collection.insert_one(cart, {"_id": 0})
    created_cart = await cart_collection.find_one({"_id": newCart.inserted_id}, {"_id": 0})
    if created_cart is None:
        return ErrorResponseModel(404, "Cart not created", "Not found")
    return ResponseModel(data=created_cart, message="Cart created successfully")

async def crud_get_cart(request: dict):
    try:
        get_beare_token = get_bearer_token(request)
        user_info = await get_current_user(get_beare_token)
        user_data = user_info.get('data')
        if not user_data:
            return ErrorResponseModel(404, "User not found", "Not found")

        cart_id = user_data[0].get('cartId')
        cart = await cart_collection.find_one({"cartId": cart_id}, {"_id": 0})
        if cart is None:
            new_cart_id = generate_cart_id()
            new_cart_data = {
                "cartId": new_cart_id,
                "products": [],
                "services": [],
                "totalPrice": 0,
                "updateAt": datetime.now(),
                "fees": {
                    "shipping": 0,
                    "tax": 0,
                    "handling": 0,
                    "voucherCode": None,
                    "voucherDiscount": None,
                },
                "totalProductQuantity": 0,
            }
            resp_create_cart = await crud_create_cart(new_cart_data)
            if resp_create_cart.get('code') != 200:
                return ErrorResponseModel(code=status.HTTP_400_BAD_REQUEST, message="Cart data not create", status="Error")
            # sync cart_id for user
            responUpdateUserCartID = await account_collection.update_one({"accountId": user_data[0].get('accountId')}, {"$set": {"cartId": new_cart_id}})
            if responUpdateUserCartID is None:
                return ErrorResponseModel(code=status.HTTP_400_BAD_REQUEST, message="Cart data not create", status="Error")
            return ResponseModel(data=new_cart_data, message="Cart data created successfully")
        else:
            cart['totalProductQuantity'] = sum([product['quantity'] for product in cart['products']])
            for product in cart['products']:
                product_data = await product_collection.find_one(
                    {
                        "productId": product['productId']
                    }, {
                        "_id": 0, "productName": 1, "picProduct": 1
                    }
                )
                product['image'] = product_data.get('picProduct').get('path')
                category_data = await category_collection.find_one(
                    {
                        "categoryId": product['categoryId']
                    }, {
                        "_id": 0, "categoryName": 1, "slug": 1
                    }
                )
                product['categoryName'] = category_data.get('categoryName')
                product['slug'] = category_data.get('slug')
            return ResponseModel(data=cart, message="Cart data retrieved successfully")
    except Exception as e:
        logging.error(e)
        return ErrorResponseModel(code=status.HTTP_400_BAD_REQUEST,  message="Have an error", status="Error")

async def crud_update_cart(request: dict, data: CartProductSchema):
    try:
        token = get_bearer_token(request)
        user_info = await get_current_user(token)
        user_data = user_info.get('data')
        if not user_data:
            return CustomJSONResponse(code=status.HTTP_404_NOT_FOUND, message="User not found", status="Error")
        cart_id = user_data[0].get('cartId')
        if not cart_id:
            return CustomJSONResponse(code=status.HTTP_404_NOT_FOUND, message="Cart not found", status="Error")
        cart = await cart_collection.find_one({"cartId": cart_id}, {"_id": 0})
        if not cart:
            # create new cart for user
            # new_cart_data = {
            #     "cartId": generate_cart_id(),
            #     "products": [],
            #     "services": [],
            #     "totalPrice": 0,
            #     "updateAt": datetime.now(),
            #     "fees": {
            #         "shipping": 0,
            #         "tax": 0,
            #         "handling": 0,
            #         "voucherCode": None,
            #         "voucherDiscount": None,
            #     },
            #     "totalProductQuantity": 0,
            # }
            # return await crud_create_cart(request, new_cart_data)
            # TODO: create then sync cart data for customer
            return CustomJSONResponse(code=status.HTTP_404_NOT_FOUND, message="Cart not found", status="Error")
        cart_products = cart['products']
        if len(cart_products) != 0:
            existing_item = next((item for item in cart['products'] if item['productId'] == data.dict().get('productId')), None)
            if existing_item is None:
                # product_data = await product_collection.find_one({"productId": data.productId}, {"_id": 0, "productName": 1, "picProduct": 1})
                category_data = await category_collection.find_one({"categoryId": data.categoryId}, {"_id": 0, "categoryName": 1, "slug": 1})

                cart_products.append({
                    "type": "",
                    "productId": data.dict().get('productId'),
                    "productName": data.dict().get('productName'),
                    "sellerName": data.dict().get('sellerName'),
                    "quantity": data.dict().get('quantity'),
                    "price": data.dict().get('price'),
                    "total": data.dict().get('quantity') * data.dict().get('price'),
                    "categoryId": data.dict().get('categoryId'),
                    "categoryName": category_data.get('category_name'),
                    "slug": category_data.get('slug'),
                    "productType": data.dict().get('productType'),
                })
                print("cart_products", cart_products)
            else:
                existing_item['quantity'] += data.dict().get('quantity')
                existing_item['total'] = existing_item['quantity'] * existing_item['price']
        else:
            # product_data = await product_collection.find_one({"productId": data.productId}, {"_id": 0, "productName": 1, "picProduct": 1})
            category_data = await category_collection.find_one({"categoryId": data.categoryId}, {"_id": 0, "categoryName": 1, "slug": 1})
            cart_products.append({
                "type": data.dict().get('type'),
                "productId": data.dict().get('productId'),
                "productName": data.dict().get('productName'),
                "sellerName": data.dict().get('sellerName'),
                "quantity": data.dict().get('quantity'),
                "price": data.dict().get('price'),
                "total": data.dict().get('quantity') * data.dict().get('price'),
                "categoryId": data.dict().get('categoryId'),
                "categoryName": category_data.get('categoryName'),
                "slug": category_data.get('slug'),
                "productType": data.dict().get('productType'),
            })

        cart['totalPrice'] = sum([product['total'] for product in cart['products']])
        cart['updateAt'] = datetime.now().isoformat()
        cart['fees'] = {
            "shipping": 0,
            "tax": 0,
            "handling": 0,
            "voucherCode": None,
            "voucherDiscount": None,
        }
        await cart_collection.update_one({"cartId": cart_id}, {"$set": cart}, upsert=True)
        return CustomJSONResponse(message="Cart updated successfully", status="OK", data=cart, code=status.HTTP_200_OK)
    except Exception as e:
        logging.error(e)
        return CustomJSONResponse(code=status.HTTP_400_BAD_REQUEST, message="Have an error, please re-check update cart", status="Error")

async def crud_remove_product(request: dict, data: RemoveCartItemSchema):
    try:
        cartId = data.dict().get('cartId')
        productId = data.dict().get('productId')
        cart = await cart_collection.find_one({"cartId": cartId}, {"_id": 0})
        if not cart:
            return ErrorResponseModel(404, "Cart not found", "Error")

        cartProducts = cart['products']
        if len(cartProducts) == 0:
            return ErrorResponseModel(404, "Cart is empty", "Not found")

        existingItem = next((item for item in cartProducts if item['productId'] == productId), None)
        if existingItem is None:
            return ErrorResponseModel(404, "Product not found in cart", "Not found")

        cart['products'].remove(existingItem)
        cart['totalPrice'] = sum([product['total'] for product in cart['products']])
        cart['updateAt'] = datetime.now()
        cart['fees'] = {
            "shipping": 0,
            "tax": 0,
            "handling": 0,
            "voucherCode": None,
            "voucherDiscount": None,
        }
        await cart_collection.update_one({"cartId": cartId}, {"$set": cart}, upsert=True)
        return ResponseModel(data=cart, message="Product removed successfully")
    except Exception as e:
        logging.error(e)
        return ErrorResponseModel(code=status.HTTP_400_BAD_REQUEST, message="Have an error", status="Error")

async def crud_update_cart_product(request: dict, data: UpdateCartProduct):
    try:
        cartId = data.dict().get('cartId')
        productId = data.dict().get('productId')
        quantity = data.dict().get('quantity')
        cart = await cart_collection.find_one({"cartId": cartId}, {"_id": 0})
        if not cart:
            return ErrorResponseModel(code=status.HTTP_404_NOT_FOUND, message="Cart not found", status="Error")

        cartProducts = cart['products']
        if len(cartProducts) == 0:
            return ErrorResponseModel(code=status.HTTP_404_NOT_FOUND, message="Cart is empty", status="Not found")

        existingItem = next((item for item in cartProducts if item['productId'] == productId), None)
        if existingItem is None:
            return ErrorResponseModel(code=status.HTTP_404_NOT_FOUND, message="Product not found in cart", status="Not found")

        existingItem['quantity'] = quantity
        existingItem['total'] = quantity * existingItem['price']
        cart['totalPrice'] = sum([product['total'] for product in cart['products']])
        cart['updateAt'] = datetime.now()
        cart['fees'] = {
            "shipping": 0,
            "tax": 0,
            "handling": 0,
            "voucherCode": None,
            "voucherDiscount": None,
        }
        await cart_collection.update_one({"cartId": cartId}, {"$set": cart}, upsert=True)
        return ResponseModel(cart, "Product updated successfully")
    except Exception as e:
        logging.error(e)
        return ErrorResponseModel(code=status.HTTP_400_BAD_REQUEST, message="Have an error", status="Error")
