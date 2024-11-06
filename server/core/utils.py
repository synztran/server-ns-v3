from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import json
from datetime import datetime
from bson import ObjectId as BsonObjectId


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        code: int = None,
        detail: Optional[str] = None,
        message: str = None,
        status: str = None,
        **kwargs
    ):
        self.custom_detail = {
            "message": message,
            "status": status,
            "code": code,
        }
        super().__init__(status_code=code, detail=self.custom_detail, headers=None, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.custom_detail})"

    def __str__(self) -> str:
        return self.__repr__()

def custom_exception_handler(request: Any, exc: CustomHTTPException) -> Dict[str, Any]:
    # return exc.custom_detail
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )

class CustomeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

class CustomJSONResponse(JSONResponse):
    def __init__(self, message: str, status: str, data: dict = None, code: int = None, **kwargs):
      # Custom structure with message, status, and data on the same level
        content = {
            "message": message,
            "status": status,
            "code": code,
        }
        if data not in [None, {}]:
            content["data"] = data
        super().__init__(status_code=code, content=content, **kwargs)

# class ObjectId(BsonObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v: Any):
#         if not BsonObjectId.is_valid(v):
#             raise ValueError("Invalid ObjectId")
#         return cls(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")

# # Add ObjectId to Pydantic's JSON encoders
# ENCODERS_BY_TYPE[BsonObjectId] = str
