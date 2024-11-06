from fastapi import APIRouter, status

router = APIRouter()

@router.get("/cards", status_code=status.HTTP_200_OK, response_description="Trả về danh sách các lá bài.")
async def get_blind_cards():
  return crud_get_blind_cards()
