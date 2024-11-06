from fastapi import APIRouter, status, Request
from server.crud.config import crud_get_config
from server.core.oauth2 import get_auth_user
from server.core.utils import CustomJSONResponse

router = APIRouter()

@router.get('', status_code=status.HTTP_200_OK, response_description="Config retrieved success.")
async def get_config(req: Request):
    # account = get_auth_user(req)
    # if account is None:
    #     return CustomJSONResponse(code=status.HTTP_401_UNAUTHORIZED, message="Unauthorized", status="error")
    return await crud_get_config()
