import json
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime

from server.database import (
    retrieveCategories,
    retrieveCategoriesByParams,
    retrieve_category_by_id,
    add_category,
    add_account
)

from server.models.category import (
    ErrorResponseModel,
    ResponseModel,
    CategorySchema,
    ParamsGet,
    StatusGB
)

router = APIRouter()

# Retrieve all category

class CustomeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


@router.get("")
async def get_all_category(status_gb: str = "", slug: str = ""):
    categories = await retrieveCategories(status_gb, slug)
    categories = jsonable_encoder(categories)
    if categories:
        return JSONResponse(
            content={
                "data": categories, 
                "code": status.HTTP_200_OK, 
                "message": "Categories data retrieve successfully", 
                "status": "OK"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"data": categories, "code": status.HTTP_200_OK, "message": "Empty list returned", status: "OK"},
        status_code=status.HTTP_200_OK
    )

@router.post("", response_description="Category data added into the database")
async def add_category_data(category: CategorySchema = Body(...)):
    category = jsonable_encoder(category)
    new_category = await add_category(category)
    return ResponseModel(new_category, "Account added successfully.")

@router.get("/{slug}", response_description="Category detail data from db")
async def get_category_by_id(slug: str):
    category = await retrieve_category_by_id(slug)
    if category:
        return ResponseModel(category, f"Category with ID {slug} retrieved successfully")
    
    raise HTTPException(status_code=404, detail=f"Category with ID {slug} not found")

@router.post("/getCategoriesByIds", response_description="Get categories by params")
async def getCategoriesByIds(params: ParamsGet):
    categories = await retrieveCategoriesByParams(params)
    categories = jsonable_encoder(categories)
    if categories:
        return JSONResponse(
            content={
                "data": categories, 
                "code": status.HTTP_200_OK, 
                "message": "Categories data retrieve successfully", 
                "status": "OK"
            },
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"data": categories, "code": status.HTTP_200_OK, "message": "Empty list returned", status: "OK"},
        status_code=status.HTTP_200_OK
    )
    return ResponseModel(params, "get categories success.")