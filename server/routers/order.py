from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.encoders import jsonable_encoder

from server.database import (
    create_order,
    retrieveOrder,
)

from server.models.order import (
    OrderSchema,
    ResponseModel,
)


router = APIRouter()

@router.get("", response_description="Order data from the db")
async def getOrderDetail(req: Request ):
    orderId = req.query_params.get('orderId')
    order = await retrieveOrder(orderId)
    if order:
        return ResponseModel(order, "Order data retrieve successfull")
    raise HTTPException(status_code=404, detail=f"Order with ID {orderId} not found")

@router.post("/checkout")
async def postCheckoutOrder(order: OrderSchema = Body(...)):
    print("order", order)
    order = jsonable_encoder(order)
    newOrder = await create_order(order)
    if not newOrder:
        raise HTTPException(status_code=500, detail="Order not created.")
    return ResponseModel(newOrder, "Order added successfully.")