from pydantic import BaseModel
from typing import Optional

class ShippingRate(BaseModel):
   fastDelivery: float
   normalDelivery: float

class ConfigSchema(BaseModel):
  shippingRate: Optional[ShippingRate] = None

  class Config:
      json_schema_extra = {
          "example": {
              "shippingRate": {
                  "fastDelivery": 10.0,
                  "normalDelivery": 5.0
              }
          }
      }
