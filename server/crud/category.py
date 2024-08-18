import motor.motor_asyncio
import pymongo
import os

from fastapi import HTTPException
from typing import List, Optional
from dotenv import load_dotenv
from uuid import uuid4
from server.core.generate import categoryHelper, generateId
from server.models.category import ParamsGet


# connect db from .env file
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
categoryCollection = database.get_collection("categories")


# Category's Functions
async def getCategoriesByParams(params: ParamsGet):
    status = params.status if params.status else ""
    slug = params.slug if params.slug else ""
    ids = params.ids if params.ids else []
    categories = []
    if status != "":
        async for category in categoryCollection.find({
            "status": {"$eq": status}
        }):
            categories.append(categoryHelper(category))
        return categories
    if slug != "":
        async for category in categoryCollection.find({
            "categoryUrlName": {"$eq": slug}
        }):
            categories.append(categoryHelper(category))
        return categories
    if len(ids) > 0:
        async for category in categoryCollection.find({
            "categoryId": {"$in": ids}
        }):
            categories.append(categoryHelper(category))
        return categories
    else:
        async for category in categoryCollection.find():
            categories.append(categoryHelper(category))
        return categories 

async def filterCategory(status: str, slug: str):
    categories = []
    if status != "":
        async for category in categoryCollection.find({
            "status": {"$eq": status}
        }):
            categories.append(categoryHelper(category))
        return categories
    if slug != "":
        async for category in categoryCollection.find({
            "categoryUrlName": {"$eq": slug}
        }):
            categories.append(categoryHelper(category))
        return categories
    else:
        async for category in categoryCollection.find():
            categories.append(categoryHelper(category))
        return categories
    
async def add_category(data: dict) -> dict:
    categoryId = await generateId("category")
    data["categoryId"] = categoryId
    category = await categoryCollection.insert_one(data)
    newCategory = await categoryCollection.find_one({"_id": category.inserted_id})
    return categoryHelper(newCategory)

async def getCategoryBySlug(slug: str):
    category = await categoryCollection.find_one({"categoryUrlName": slug})

    if category:
        return categoryHelper(category)

    raise HTTPException(status_code=404, detail=f"Category with slug: {slug} not found")