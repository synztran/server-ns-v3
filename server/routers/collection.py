from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from server.models.product import (
    ErrorResponseModel,
    ResponseModel,
    ProductSchema,
)

router = APIRouter()

# API for Collection
