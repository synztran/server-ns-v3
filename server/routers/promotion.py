
from fastapi import APIRouter, Request, status
from server.core.oauth2 import get_auth_user
from server.models.promotion import ResponseError
from server.crud.promotion import crud_get_lucky_wheel_data

router = APIRouter()

@router.get("/lucky-wheel/get", response_description="Get lucky wheel data")
async def get_lucky_wheel_data(request: Request):
    return await crud_get_lucky_wheel_data()
