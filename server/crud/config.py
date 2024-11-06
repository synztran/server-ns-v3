import os
from dotenv import load_dotenv
import motor.motor_asyncio
from fastapi import status
from server.core.database import config_helper
from server.core.utils import CustomJSONResponse

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
config_collection = database.get_collection("configs")


async def crud_get_config():
    config = await config_collection.find_one({},{"_id": 0})
    if config:
        return CustomJSONResponse(data=config_helper(config), message="Retrieved success", status="OK", code=status.HTTP_200_OK)
    return CustomJSONResponse(message="Config not found", status="error", code=status.HTTP_404_NOT_FOUND)
