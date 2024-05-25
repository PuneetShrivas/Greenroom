from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import approuter
from data.preprocessing.main import preprocessing_scripts

preprocessing_scripts()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this according to your requirements
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(approuter)
