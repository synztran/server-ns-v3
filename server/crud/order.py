from fastapi import Request, HTTPException
from dotenv import load_dotenv
import os
import motor.motor_asyncio
from server.core.database import order_helper
from server.models.order import ResponseModel, EnumOrderPaymentStatus, EnumOrderStatus
from fastapi.encoders import jsonable_encoder
from typing import Union
from server.core.generate import generate_order_id
from datetime import datetime
from uuid import uuid4
from server.core.utils import CustomJSONResponse, CustomHTTPException

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
order_collection = database.get_collection("orders")
account_collection = database.get_collection("accounts")

# main
async def retrieve_order(order_id: str):
    order = await order_collection.find_one({"orderId": order_id})
    if order:
        return order_helper(order)
    return None

async def create_order(order_data: dict) -> Union[dict, None]:
    try:
        order_id = await generate_order_id(order_data["services"], order_data["products"])
        order_data["orderId"] = order_id
        order_data["totalPrice"] = order_data["totalPrice"]
        order_data['orderedAt'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orderTotalQuantity = sum(product["quantity"] for product in order_data['products'])
        order_data['totalQuantity'] = orderTotalQuantity if orderTotalQuantity > 0 else 0
        order_data['paymentStatus'] = EnumOrderPaymentStatus.PENDING.value
        order_data['orderStatus'] = EnumOrderStatus.ORDERED.value

        order = await order_collection.insert_one(order_data)
        new_order = await order_collection.find_one({"_id": order.inserted_id})
        if new_order:
            cart = await account_collection.find_one({"cartId": order_data["cartId"]})
            if cart:
                # clear cart data when new order is created
                await account_collection.update_one(
                    {"cartId": order_data["cartId"]},
                    {"$set": {
                        "cartId": str(uuid4()),
                        "products": [],
                        "services": [],
                        "updatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "totalPrice": 0,
                        "fees": {
                            "shipping": 0,
                            "tax": 0,
                            "handling": 0,
                            "voucherCode": "",
                            "voucherDiscount": 0
                        }
                    }}
                )
        else:
            return None
        return order_helper(new_order)
    except Exception as e:
        print("Error: ", e)
        return CustomJSONResponse(status_code=500, content={"message": "Error creating order"})

async def update_order(order_id: str, new_data: dict):
    # Return false if an empty request body is sent.
    if len(new_data) < 1:
        return False
    order = await order_collection.find_one({"orderId": order_id})
    if order is None:
        return False

    updated_order = await order_collection.update_one(
        {"orderId": order_id}, {"$set": new_data}
    )
    if updated_order:
        return True
    return False

async def crud_get_order_detail(req: Request):
    order_id = req.query_params.get('orderId')
    order = await retrieve_order(order_id)
    if order:
        return ResponseModel(order, "Order data retrieve successfull")
    raise CustomHTTPException(status_code=404, message=f"Order with ID {order_id} not found", status="Error")

async def crud_post_checkout_order(order: dict):
    order = jsonable_encoder(order)
    newOrder = await create_order(order)
    if not newOrder:
        raise CustomHTTPException(status_code=500, message="Order not created.", status="Error")
    return ResponseModel(newOrder, "Order added successfully.")
