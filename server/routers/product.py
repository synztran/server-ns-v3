from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder
import asyncio
from bson import ObjectId


from server.database import (
    retrieve_products,
    add_product,
    retrieve_product_by_id,
    retrieve_products_by_id,
    retrieve_product_opts,
    retrieveProductByParams
)
# from app.server.models.student import (
from server.models.productOption import ParamsGet as ProductOptionParamsGet
from server.models.product import (
    ErrorResponseModel,
    ResponseModel,
    ProductSchema,
)

router = APIRouter()

# Retrieve all acount

@router.get("", response_description="Products data from the database")
async def get_all_product():
    products = await retrieve_products()
    if products:
        return ResponseModel(products, "Products data retrieve successfully")
    return ResponseModel(products, "Empty list returned")


@router.post("", response_description="Product data added into the database")
async def add_product_data(product: ProductSchema = Body(...)):
    product = jsonable_encoder(product)
    new_product = await add_product(product)
    return ResponseModel(new_product, "Product added successfully.")

@router.get("/{product_id}", response_description="Product data from the db")
async def get_product_detail(product_id: str):
    product = await retrieve_product_by_id(product_id)

    if product:
        return ResponseModel(product, "Product data retrieve successfull")
    raise HTTPException(status_code=404, detail=f"product with ID {product_id} not found")

@router.get("/all/{category_id}", response_description="Products data from db")
async def get_products_by_id(category_id: str):
    async def process_product(product):
        product_id = product.get('product_id')
        productOpts = await retrieve_product_opts(product_id)
        # Append newArray to the product dictionary
        if isinstance(productOpts, ObjectId):
            productOpts = [productOpts]
        
        product['productOpts'] = productOpts
         # Append the product to the final list

    products = await retrieve_products_by_id(category_id)

    # Use asyncio.gather to call process_product for each product concurrently
    await asyncio.gather(*[process_product(product) for product in products])

    if products:
        return ResponseModel(products, "Products data retrieve successfull")
    raise HTTPException(status_code=404, detail=f"products with ID {category_id} not found")

@router.post("/get-by-params", response_description="Product options data from the db")
async def get_product_opts_by_param(params: ProductOptionParamsGet):
    productOpts = await retrieveProductByParams(params)
    if productOpts:
        return ResponseModel(productOpts, "Product options data retrieve successfull")
    return ResponseModel(productOpts, "Empty list returned")
