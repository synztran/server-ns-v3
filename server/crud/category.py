import motor.motor_asyncio
import pymongo
import os

from fastapi import HTTPException, status
from typing import List
from dotenv import load_dotenv
from server.models.category import ParamsGet, ResponseModel
from server.core.database import category_helper
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from server.core.generate import generate_id


# connect db from .env file
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
category_collection = database.get_collection("categories")

# Category's Functions
async def get_categories_by_params(params: ParamsGet):
    print("params", params)
    status = params.status if params.status else ""
    slug = params.slug if params.slug else ""
    ids = params.ids if params.ids else []
    print("slug", slug)
    categories = []
    if status != "":
        async for category in category_collection.find({
            "status": {"$eq": status}
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
            "categoryId": {"$in": ids}
        }):
            categories.append(category_helper(category))
        return categories
    else:
        async for category in category_collection.find():
            categories.append(category_helper(category))
        return categories

async def filter_category(status: str, slug: str):
    categories = []
    if status != "":
        async for category in category_collection.find({
            "status": {"$eq": status}
        }):
            categories.append(category_helper(category))
        return categories
    if slug != "":
        async for category in category_collection.find({
            "categoryUrlName": {"$eq": slug}
        }):
            categories.append(category_helper(category))
        return categories
    else:
        async for category in category_collection.find():
            categories.append(category_helper(category))
        return categories

async def add_category(data: dict) -> dict:
    category_id = await generate_id("category")
    data["categoryId"] = category_id
    category = await category_collection.insert_one(data)
    new_category = await category_collection.find_one({"_id": category.inserted_id})
    return category_helper(new_category)

async def get_category_by_slug(slug: str):
    category = await category_collection.find_one({"slug": slug})
    if category:
        return category_helper(category)
    raise HTTPException(status_code=404, detail=f"Category with slug: {slug} not found")

async def retrieve_categories(status_gb: str, slug: str):
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

async def retrieve_categories_by_params(params: ParamsGet):
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

async def retrieve_category_by_id(slug: str):
    category = await category_collection.find_one({"slug": slug})
    if category:
        return category_helper(category)
    raise HTTPException(status_code=404, detail=f"Category with ID {slug} not found")

# crud
async def crud_get_all_category(request: ParamsGet) -> List[dict]:
    req_status_gb = request.statusGb if request.statusGb != "" else ""
    req_slug = request.slug if request.slug else ""
    categories = await retrieve_categories(req_status_gb, req_slug)
    categories = jsonable_encoder(categories)
    if categories is None:
        return JSONResponse(
            content={
                "data": categories,
                "code": status.HTTP_200_OK,
                "message": "Empty list returned",
                status: "OK"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "data": categories,
            "code": status.HTTP_200_OK,
            "message": "Categories data retrieve successfully",
            "status": "OK"
        },
        status_code=status.HTTP_200_OK
    )

async def crud_add_category(request: dict) -> dict:
    category = jsonable_encoder(request)
    new_category = await add_category(category)
    return ResponseModel(new_category, "Account added successfully.")

async def crud_get_category_by_id(request: str) -> dict:
    category = await get_category_by_slug(request)
    if category:
        return ResponseModel(category, f"Category with ID {request} retrieved successfully")
    raise HTTPException(status_code=404, detail=f"Category with ID {request} not found")

async def crud_get_categories_by_ids(request: ParamsGet) -> List[dict]:
    categories = await retrieve_categories_by_params(request)
    categories = jsonable_encoder(categories)
    if categories is None:
        return JSONResponse(
            content={
                "data": categories,
                "code": status.HTTP_200_OK,
                "message": "Empty list returned",
                status: "OK"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={
            "data": categories,
            "code": status.HTTP_200_OK,
            "message": "Categories data retrieve successfully",
            "status": "OK"
        },
        status_code=status.HTTP_200_OK
    )
