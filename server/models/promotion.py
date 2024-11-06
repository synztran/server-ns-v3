from fastapi import status
from datetime import datetime
from pydantic import BaseModel
from enum import Enum
from bson import ObjectId
from typing import List

class PromotionType(Enum):
    LUCKY_WHEEL = "lucky_wheel"

class LuckyWheelItem(BaseModel):
    _id: ObjectId
    isNotify: bool = False
    createdBy: int = 0
    isActive: bool = False
    itemName: str = ""
    index: int = 0
    itemDescription: str = ""
    createdAt: datetime = datetime.now()
    luckyWheelCode: str = ""
    percentage: float = 0.0
    backgroundColor: str = ""
    maxQuantityPerCustomer: int = 0
    contentNotify: str = ""
    itemCode: str = ""
    maxQuantity: int = 0
    itemUrl: str = ""
    maxQuantityPerDay: int = 0

class LuckyWheel(BaseModel):
    _id: ObjectId
    isActive: bool = False
    hashTag: str = ""
    imageTitleWeb: str = ""
    mainImage: str = ""
    createdAt: datetime = datetime.now()
    type: PromotionType = PromotionType.LUCKY_WHEEL
    isFreeTurn: bool = False
    timeToFreeTurn: int = 0
    bannerMobile: str = ""
    description: str = ""
    imageTitleMobile: str = ""
    mainImageMobile: str = ""
    endAt: datetime
    bannerWeb: str = ""
    createdBy: int = 0
    code: str = ""
    backgroundMobile: str = ""
    name: str = ""
    startAt: datetime
    versionUpdate: str = ""
    backgroundWeb: str = ""
    lastUpdatedAt: datetime
    rewards: List[LuckyWheelItem] = []

def ResponseSuccess(data, message):
    return {
        "data": [data],
        "code": status.HTTP_200_OK,
        "message": message,
    }

def ResponseError(code, message):
    return {
        "code": code,
        "message": message,
    }
