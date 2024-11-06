import os
import motor.motor_asyncio
from fastapi import status
from dotenv import load_dotenv
from server.models.promotion import ResponseError, ResponseSuccess, LuckyWheel, LuckyWheelItem, PromotionType

# variables
totalItems = 12

# load env
load_dotenv()
MONGO_DETAILS = os.environ.get('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
lucky_wheel_collection = database.get_collection("lucky_wheels")
lucky_wheel_item_collection = database.get_collection("lucky_wheel_items")


# crud

async def crud_get_lucky_wheel_data():
    lucky_wheel = await lucky_wheel_collection.find_one({},{ '_id': 0})
    if lucky_wheel is None:
        return ResponseError(status.HTTP_404_NOT_FOUND, "Không tìm thấy dữ liệu")

    # Ensure the type is set to LUCKY_WHEEL
    lucky_wheel['type'] = PromotionType.LUCKY_WHEEL
    lucky_wheel = LuckyWheel(**lucky_wheel)
    lucky_wheel_code = lucky_wheel.code
    lucky_wheel_items = await lucky_wheel_item_collection.find({"luckyWheelCode": lucky_wheel_code}, {'_id': 0}).to_list(length=totalItems)

    if len(lucky_wheel_items) == 0:
        return ResponseError(status.HTTP_404_NOT_FOUND, "Không tìm thấy dữ liệu")

    lucky_wheel_items = [LuckyWheelItem(**item) for item in lucky_wheel_items]
    lucky_wheel.rewards = lucky_wheel_items
    return ResponseSuccess(lucky_wheel, "Lấy dữ liệu thành công")
