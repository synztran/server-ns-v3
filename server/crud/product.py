import os
import motor.motor_asyncio
import asyncio

from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from server.models.product import ResponseModel, ErrorResponseModel
from server.core.generate import generate_id
from server.core.database import product_helper
from bson import ObjectId

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
product_collection = database.get_collection("products")
product_option_collection = database.get_collection("productOptions")

# def
async def add_product(product_data: dict) -> dict:
    product_id = await generate_id("product")
    product_data["productId"] = product_id
    product = await product_collection.insert_one(product_data)
    new_product = await product_collection.find_one({"_id": product.inserted_id})
    return product_helper(new_product)

async def retrieve_product_opts(product_id):
    product_opts = []
    # Assuming 'product_id' is the field in the collection
    query = {"productId": product_id}
    projection = {"_id": 0}  # Exclude _id
    async for option in product_option_collection.find(query, projection):
        product_opts.append(option)
    if product_opts is None:
        return []
    return product_opts

async def retrieve_products_by_id(category_id: str):
    print("category_id", category_id)
    products = []
    async for product in product_collection.find({"categoryId": category_id}):
        products.append(product_helper(product))

    if products:
        return products

    raise HTTPException(status_code=404, detail=f"All Product with ID {category_id} not found")

async def retrieve_product_by_params(params: dict):
    ids = params.ids if params.ids else []
    products = []
    if len(ids) > 0:
        async for product in product_collection.find({
            "productId": {"$in": ids}
        }):
            products.append(product_helper(product))
        return products
    else:
        async for product in product_collection.find():
            products.append(product_helper(product))
        return products

# crud
async def crud_get_all_product():
    products = []
    async for product in product_collection.find({}, {"_id": 0}):
        products.append(product)
    if products is None:
        return ErrorResponseModel(error="An error occurred", code=404, message="Fail to retrieve products.")
    return ResponseModel(products, "Products data retrieve successfull")

async def crud_post_add_product_data(product: dict):
    product = jsonable_encoder(product)
    new_product = await add_product(product)
    if new_product is None:
        return ErrorResponseModel(error="An error occurred", code=404, message="Fail to add product.")
    return ResponseModel(new_product, "Product added successfully.")

async def crud_get_product_detail(product_id: str):
    product = await product_collection.find_one({"product_id": product_id})
    if product is None:
        return ErrorResponseModel(error="An error occurred", code=404, message="Product not found.")
    return product_helper(product)

async def crud_get_products_by_id(category_id: str):
    async def process_product(product):
        product_id = product.get('productId')
        product_opts = await retrieve_product_opts(product_id)
        # Append newArray to the product dictionary
        if isinstance(product_opts, ObjectId):
            product_opts = [product_opts]

        product['productOpts'] = product_opts
         # Append the product to the final list

    products = await retrieve_products_by_id(category_id)

    # Use asyncio.gather to call process_product for each product concurrently
    await asyncio.gather(*[process_product(product) for product in products])

    if products:
        return ResponseModel(products, "Products data retrieve successfull")
    raise HTTPException(status_code=404, detail=f"products with ID {category_id} not found")

async def crud_get_product_opts_by_param(params: dict):
    product_opts = await retrieve_product_by_params(params)
    if product_opts is None:
        return ResponseModel(product_opts, "Empty list returned")
    return ResponseModel(product_opts, "Product options data retrieve successfull")
