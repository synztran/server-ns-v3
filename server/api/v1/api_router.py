from fastapi import APIRouter
from server.api.v1.endpoint.user import user

#---------------------------------------------#

apiRouter = APIRouter()
apiRouter.include_router(user.router, prefix='/users', tags=['users'])
