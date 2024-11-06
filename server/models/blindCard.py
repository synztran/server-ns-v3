from typing import List, Enum
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class EnumCardType(str, Enum):
  ITEM = "ITEM"
  MONEY = "MONEY"
  LUCKY = "LUCKY"

class Reward(BaseModel):
  rewardId: str
  rewardName: str
  rewardValue: int
  rewardDescription: str
  link: str

class BlindCard(BaseModel):
  cardId: str
  cardName: str
  cardNumber: str
  cardType: EnumCardType
  createdAt: datetime
  isActive: bool = False
  reward: Reward
  isOpen: bool = False

class Config:
  json_schema_extra = {
    "example": {
      "cardId": "abc",
      "cardName": "Hari",
      "cardNumber": "123456789",
      "cardType": "ITEM",
      "createdAt": "2021-07-01T00:00:00",
      "isActive": False,
      "reward": {
        "rewardId": "abc",
        "rewardName": "Hari",
        "rewardValue": 100,
        "rewardDescription": "Hari",
        "link": "https://hari.com"
      },
      "isOpen": False
    }
  }

  def ResponseModel(data, message):
    return {
      "data": [data],
      "code": 200,
      "message": message
    }

  def ErrorResponseModel(code, message):
    return {
      "code": code,
      "message": message,
      "status": "ERROR"
    }
