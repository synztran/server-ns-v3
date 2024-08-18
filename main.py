from fastapi import FastAPI

import uvicorn

app = FastAPI()


# class Item(BaseModel):
#     name: str
#     price: float
#     is_offer: Union[bool, None] = None


if __name__  == "__main__":
    uvicorn.run("server.app:app", host="0.0.0.0", port=8000, reload=True)

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


# @app.put("/item/{item_id}")
# def update_item(item_id: int, item: Item):
#     return {"item_name": item.name, "item_id": item_id}