from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import approuter



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this according to your requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approuter)

# @app.post("/dress_description/")
# async def get_dress_description():
#     try:
#         return JSONResponse({"description":"hello"})
#     except HTTPException as e:
#         raise e  # Re-raise the HTTPException
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal server error")