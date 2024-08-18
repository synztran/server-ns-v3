import os
import motor.motor_asyncio
from fastapi import APIRouter, Response, status, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from uuid import uuid4
from datetime import datetime
from server.routers.user import get_current_user
from server.oauth2 import getBearerToken, decode_token
from dotenv import load_dotenv

from server.models.cart import CartSchema, CartProductSchema, ErrorResponseModel, ResponseModel, ResponeSuccessMessage, RemoveCartItemSchema, UpdateCartProduct
import logging


# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

#collection
cartCollection = database.get_collection("carts")
categoryCollection = database.get_collection("categories")
productCollection = database.get_collection("products")
router = APIRouter()

# helper
def fixObjectId(document):
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document

@router.post("/create", response_description="create new cart", response_model=CartSchema)
async def createCart(req: Request):
    cart = jsonable_encoder(req)
    print("end code", cart)
    newCart = await cartCollection.insert_one(cart, {"_id": 0})
    createdCart = await cartCollection.find_one({"_id": newCart.inserted_id})
    createdCart = fixObjectId(createdCart)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=createdCart)

@router.get("", response_description="Get cart by id")
async def getCart(req: Request, response: Response):
    try:
        getBeareToken = getBearerToken(req)
        userInfo = await get_current_user(getBeareToken)
        userData = userInfo.get('data')
        if not userData:
            return ErrorResponseModel(404, "User not found")
        cartId = userData[0].get('cartId')
        print("cartId: ", cartId)
        cart = await cartCollection.find_one({"cartId": cartId}, {"_id": 0})
        cart = fixObjectId(cart) # convert ObjectId to string
        if cart is None:
            print("run here")
            newCartData = {
                "cartId": cartId,
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
            # await createCart(req, newCartData)
            await createCart(newCartData)
            return ResponseModel(newCartData, "Cart data retrieved successfully")
        else:
            cart['totalProductQuantity'] = sum([product['quantity'] for product in cart['products']])
            for product in cart['products']:
                productData = await productCollection.find_one({"product_id": product['productId']}, {"_id": 0, "product_name": 1, "pic_product": 1})
                product['image'] = productData.get('pic_product').get('path')
                categoryData = await categoryCollection.find_one({"category_id": product['categoryId']}, {"_id": 0, "category_name": 1, "slug": 1})
                product['categoryName'] = categoryData.get('category_name')
                product['slug'] = categoryData.get('slug')

            return ResponseModel(cart, "Cart data retrieved successfully")
    except Exception as e:
        logging.error(e)
        return ErrorResponseModel(404, "Cart not found")
        
   
@router.put("", response_description="Update cart by id")
async def update_cart(req: Request, data: CartProductSchema):
    print("data: ", data.dict())
    cartId = data.dict().get('cartId')
    print("cartId: ", cartId)
    if not cartId:
        return ErrorResponseModel(404, "Cart not found")
    cart = await cartCollection.find_one({"cartId": cartId}, {"_id": 0})
    if not cart:
        # create new cart for user
        newCartData = {
            "cartId": cartId,
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
        return await createCart(req, newCartData)
    cartProducts = cart['products']
    if len(cartProducts) != 0:
        existingItem = next((item for item in cart['products'] if item['productId'] == data.dict().get('productId')), None)
        if existingItem:
            existingItem['quantity'] += data.dict().get('quantity')
            existingItem['total'] = existingItem['quantity'] * existingItem['price']
        else:
            productData = await productCollection.find_one({"product_id": data.productId}, {"_id": 0, "product_name": 1, "pic_product": 1})
            categoryData = await categoryCollection.find_one({"category_id": data.categoryId}, {"_id": 0, "category_name": 1, "slug": 1})

            cart['products'].append({
                "type": data.dict().get('type'),
                "productId": data.dict().get('productId'),
                "productName": data.dict().get('productName'),
                "sellerName": data.dict().get('sellerName'),
                "quantity": data.dict().get('quantity'),
                "price": data.dict().get('price'),
                "total": data.dict().get('quantity') * data.dict().get('price'),
                "categoryId": data.dict().get('categoryId'),
                "image": productData.get('pic_product').get('path'),
                "categoryName": categoryData.get('category_name'),
                "slug": categoryData.get('slug'),
            })
    else:
        productData = await productCollection.find_one({"product_id": data.productId}, {"_id": 0, "product_name": 1, "pic_product": 1})
        categoryData = await categoryCollection.find_one({"category_id": data.categoryId}, {"_id": 0, "category_name": 1, "slug": 1})
        cart['products'].append({
            "type": data.dict().get('type'),
            "productId": data.dict().get('productId'),
            "productName": data.dict().get('productName'),
            "sellerName": data.dict().get('sellerName'),
            "quantity": data.dict().get('quantity'),
            "price": data.dict().get('price'),
            "total": data.dict().get('quantity') * data.dict().get('price'),
            "categoryId": data.dict().get('categoryId'),
            "image": productData.get('pic_product').get('path'),
            "categoryName": categoryData.get('category_name'),
            "slug": categoryData.get('slug'),
        })
    
    cart['totalPrice'] = sum([product['total'] for product in cart['products']])
    cart['updateAt'] = datetime.now()
    cart['fees'] = {
        "shipping": 0,
        "tax": 0,
        "handling": 0,
        "voucherCode": None,
        "voucherDiscount": None,
    }

    cartCollection.update_one({"cartId": cartId}, {"$set": cart}, upsert=True)
    return ResponeSuccessMessage("Cart updated successfully")

@router.put("/remove-item", response_description="Remove product from cart")
async def removeProduct(req: Request, data: RemoveCartItemSchema):
    cartId = data.dict().get('cartId')
    productId = data.dict().get('productId')
    cart = await cartCollection.find_one({"cartId": cartId}, {"_id": 0})
    if not cart:
        return ErrorResponseModel(404, "Cart not found")
    cartProducts = cart['products']
    if len(cartProducts) == 0:
        return ErrorResponseModel(404, "Cart is empty")
    existingItem = next((item for item in cartProducts if item['productId'] == productId), None)
    if existingItem:
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
        cartCollection.update_one({"cartId": cartId}, {"$set": cart}, upsert=True)
        return ResponseModel(cart, "Product removed successfully")
    return ErrorResponseModel(404, "Product not found in cart")

@router.put("/update-cart-product", response_description="Update product quantity in cart")
async def updateCartProduct(req: Request, data: UpdateCartProduct):
    cartId = data.dict().get('cartId')
    productId = data.dict().get('productId')
    quantity = data.dict().get('quantity')
    cart = await cartCollection.find_one({"cartId": cartId}, {"_id": 0})
    if not cart:
        return ErrorResponseModel(404, "Cart not found")
    cartProducts = cart['products']
    if len(cartProducts) == 0:
        return ErrorResponseModel(404, "Cart is empty")
    existingItem = next((item for item in cartProducts if item['productId'] == productId), None)
    if existingItem:
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
        cartCollection.update_one({"cartId": cartId}, {"$set": cart}, upsert=True)
        return ResponseModel(cart, "Product updated successfully")
    return ErrorResponseModel(404, "Product not found in cart")