from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routers.user import router as AccountRouter
from server.routers.category import router as CategoryRouter
from server.routers.product import router as ProductRouter
from server.routers.auth import router as AuthRouter
from server.routers.cart import router as CartRouter
from server.api.v1.endpoint import user
from server.routers.order import router as OrderRouter

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.include_router(AccountRouter, tags=["Account"], prefix="/account")
app.include_router(CategoryRouter, tags=["Category"], prefix="/category")
app.include_router(ProductRouter, tags=["Product"], prefix="/product")
app.include_router(AuthRouter, tags=["Auth"], prefix="/auth")
app.include_router(CartRouter, tags=["Cart"], prefix="/cart")
app.include_router(user.router, tags=["User"], prefix="/users")
app.include_router(OrderRouter, tags=["Order"], prefix="/order")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!", "version": app.version}
