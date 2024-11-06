from fastapi import APIRouter, Body
from server.models.category import (
    CategorySchema,
    ParamsGet,
)
from server.crud.category import (
    crud_get_all_category,
    crud_add_category,
    crud_get_category_by_id,
    crud_get_categories_by_ids
)

router = APIRouter()

@router.get("/get-all", response_description="Categories data retrieved")
async def get_all_category(status_gb: str = "", slug: str = ""):
   return await crud_get_all_category(ParamsGet(status_gb=status_gb, slug=slug))

@router.post("/add", response_description="Category data added into the database")
async def add_category_data(category: CategorySchema = Body(...)):
    return await crud_add_category(category)

@router.get("/{slug}", response_description="Category detail data from db")
async def get_category_by_id(slug: str):
    return await crud_get_category_by_id(slug)

@router.post("/getCategoriesByIds", response_description="Get categories by params")
async def get_categories_by_ids(params: ParamsGet):
    return await crud_get_categories_by_ids(params)
