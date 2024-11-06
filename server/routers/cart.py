import os
import motor.motor_asyncio
from fastapi import APIRouter, Response, Request
from dotenv import load_dotenv
from server.models.cart import CartSchema, CartProductSchema, RemoveCartItemSchema, UpdateCartProduct
from server.crud.cart import (
    crud_create_cart,
    crud_get_cart,
    crud_update_cart,
    crud_remove_product,
    crud_update_cart_product
)

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

@router.post("/create", response_description="create new cart", response_model=CartSchema)
async def create_cart(req: Request):
   return await crud_create_cart(req)

@router.get("", response_description="Get cart data of user")
async def getCart(req: Request, response: Response):
   return await crud_get_cart(req)

@router.put("", response_description="Update cart by id")
async def update_cart(req: Request, data: CartProductSchema):
    return await crud_update_cart(req, data)

@router.put("/remove-item", response_description="Remove product from cart")
async def removeProduct(req: Request, data: RemoveCartItemSchema):
    return await crud_remove_product(req, data)

@router.put("/update-cart-product", response_description="Update product quantity in cart")
async def updateCartProduct(req: Request, data: UpdateCartProduct):
    return await crud_update_cart_product(req, data)
