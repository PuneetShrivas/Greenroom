from typing import Dict
from fastapi import File, UploadFile, HTTPException
import requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .functions import get_review_from_user_id
import sys
sys.path.append("..")

from core import get_abs_path
import pandas as pd
import os
import dotenv
dotenv.load_dotenv()

df = pd.read_csv(get_abs_path("prompts.csv",__file__))
prompts_by_section = df.set_index('Section')['Prompt'].to_dict()

class get_review(BaseModel): #called with query, history and dress description, should stream the response out, use RAG
    async def process(self, dress_description: str, query: str, user_id: str, lat_long:dict):
        try:
            chat_history=[]
            prompts_dict = prompts_by_section
            response = get_review_from_user_id(prompts_dict,query,dress_description,chat_history,user_id,lat_long)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    class Input(BaseModel):
        query: str
        file: UploadFile = File(...)