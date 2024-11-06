from fastapi import APIRouter, status
from server.models.schemas import Token
from server.models.user import CreateUserSchema, LoginUserSchema, VerifyMailSchema
from server.crud.auth import crud_create_user, crud_login_user
from server.core.oauth2 import mail_verify_token

router = APIRouter()

@router.post('/register', status_code=status.HTTP_201_CREATED, response_description="Tài khoản đã được tạo thành công.")
async def create_user(payload: CreateUserSchema):
    return await crud_create_user(payload)

@router.post('/login')
async def login(payload: LoginUserSchema) -> Token:
    return await crud_login_user(payload)

@router.post('/verify')
async def verify_mail(payload: VerifyMailSchema):
    return mail_verify_token(payload)
