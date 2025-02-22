from fastapi import APIRouter



router = APIRouter(prefix="", tags=["Hello World"])

@router.get("/")
async def get_root():   
    return {"message": "Hello World"}
