from fastapi import APIRouter, Body, Request

from server.crud.order import (
    crud_get_order_detail,
    crud_post_checkout_order
)

from server.models.order import (
    OrderSchema,
)

router = APIRouter()

@router.get("", response_description="Order data from the db")
async def getOrderDetail(req: Request ):
   return await crud_get_order_detail(req)

@router.post("/checkout")
async def postCheckoutOrder(order: OrderSchema = Body(...)):
    return await crud_post_checkout_order(order)
