from typing import Dict
from fastapi import File, UploadFile
import requests
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
sys.path.append("..")
from .functions import create_payload, preprocess_image
from core import get_abs_path
import pandas as pd
import os
import dotenv
dotenv.load_dotenv()

df = pd.read_csv(get_abs_path("prompts.csv",__file__))
prompts_by_section = df.set_index('Section')['Prompt'].to_dict()

api_key = os.getenv("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

class get_dress_description(BaseModel):
    async def process(self, file: UploadFile):
        processed_image = await preprocess_image(file)
        payload = create_payload(processed_image,prompts_by_section["runner"])
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        description = response.json()["choices"][0]["message"]["content"]
        usage = response.json()["usage"]
        return {"description": description, "usage": usage}
    
    class Input(BaseModel):
        file: UploadFile = File(...)
        
class say_hello(BaseModel):
    async def process(self, streeng:str):
        return({"text":"hello {0}".format(streeng)})
    
    class Input(BaseModel):
        streeng: str