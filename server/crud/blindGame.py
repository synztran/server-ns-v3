import os
import motor.motor_asyncio
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from dotenv import load_dotenv

# static file
SECRET_KEY = os.getenv("JWT_HEX32")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRES_IN = os.getenv("ACCESS_TOKEN_EXPIRES_IN")

# access db
load_dotenv()
MONGO_DETAILS = os.getenv("DATABASE_URL")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.testmongodb

# collection
blindGame_collection = database.get_collection("blindGames")

# crud def
async def get_blind_cards(request: dict):
  req = jsonable_encoder(request)
  print(req)
  list_cards = []
  async for card in blindGame_collection.find(req):
    list_cards.append(card)

  if len(list_cards) == 0:
    return {"message": "Không tìm thấy lá bài nào."}
  return list_cards

async def post_pick_card(request: dict):
  req = jsonable_encoder(request)
  # base on % of each card, then random pick one
  # then update the card to be picked
  list_cards = []
  async for card in blindGame_collection.find(req):
    list_cards.append(card)
  if len(list_cards) == 0:
    return {"message": "Không tìm thấy lá bài nào."}
  # pick one
  new_card = list_cards[0]
  new_card['isPicked'] = True
  new_card['pickedAt'] = datetime.now()
  new_card['pickedBy'] = req['pickedBy']
  # update the card
  await blindGame_collection.update_one({"_id": new_card['_id']}, {"$set": new_card})

  return new_card
