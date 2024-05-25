from typing import Dict
from fastapi import File, UploadFile
import requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
sys.path.append("..")

from core import get_abs_path
import pandas as pd
import os
import dotenv
dotenv.load_dotenv()

df = pd.read_csv(get_abs_path("prompts.csv",__file__))
prompts_by_section = df.set_index('Section')['Prompt'].to_dict()

class get_review(BaseModel):
    async def process(self, file: UploadFile, query: str):
        if(len(query.strip())==0):
            query = prompts_by_section["template_query"]
        return {"description": query, "usage": "usage"}
    
    class Input(BaseModel):
        query: str
        file: UploadFile = File(...)