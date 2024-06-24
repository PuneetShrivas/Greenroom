from typing import Dict, List
from fastapi import File, UploadFile, HTTPException, Body
import requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
from .functions import get_q_and_p
import sys
sys.path.append("..")

from core import get_abs_path
import pandas as pd
import os
import dotenv
dotenv.load_dotenv()

class Queries(BaseModel):
    chat_history: List = []

df = pd.read_csv(get_abs_path("prompts.csv",__file__))
prompts_by_section = df.set_index('Section')['Prompt'].to_dict()

class get_questions_and_products(BaseModel): #called with query, history and dress description, should stream the response out, use RAG
    async def process(self, products_n:int, questions_n:int, gender_female:bool, response_strings:Queries=Body(...)):
        try:
            prompts_dict = prompts_by_section
            response = get_q_and_p(prompts_dict, response_strings, products_n, questions_n,gender_female)
            return {"response": response}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    class Input(BaseModel):
        query: str
        file: UploadFile = File(...)