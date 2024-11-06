from fastapi import APIRouter, Body

# from app.server.models.student import (
from server.models.productOption import ParamsGet as ProductOptionParamsGet
from server.models.product import (
    ProductSchema,
)

from server.crud.product import (
    crud_get_all_product,
    crud_post_add_product_data,
    crud_get_product_detail,
    crud_get_products_by_id,
    crud_get_product_opts_by_param
)

router = APIRouter()

# Retrieve all acount

# GET
@router.get("/get-all", response_description="Products data from the database")
async def get_all_product():
   return await crud_get_all_product()

@router.get("/{product_id}", response_description="Product data from the db")
async def get_product_detail(product_id: str):
   return await crud_get_product_detail(product_id)

@router.get("/all/{category_id}", response_description="Products data from db")
async def get_products_by_id(category_id: str):
    print("category_id", category_id)
    return await crud_get_products_by_id(category_id)

# POST
@router.post("", response_description="Product data added into the database")
async def add_product_data(product: ProductSchema = Body(...)):
   return await crud_post_add_product_data(product)

@router.post("/get-by-params", response_description="Product options data from the db")
async def get_product_opts_by_param(params: ProductOptionParamsGet):
    return await crud_get_product_opts_by_param(params)
