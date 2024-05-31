from typing import Dict
from fastapi import File, UploadFile, Body
import requests
from tempfile import NamedTemporaryFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from .functions import process_image, get_suggested_colors, define_season, preprocess_image, create_payload
import sys
sys.path.append("..")
from core import get_abs_path
import pandas as pd
import os
import dotenv
import csv
import json
dotenv.load_dotenv()

df = pd.read_csv(get_abs_path("prompts.csv",__file__)   )
prompts_by_section = df.set_index('Section')['Prompt'].to_dict()

api_key = os.getenv("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

class detect_season_from_image_functions(BaseModel):
    async def process(self, file: UploadFile):
        # Save the uploaded file temporarily
        with NamedTemporaryFile(delete=False) as temp_image:
            temp_image.write(await file.read())
            temp_image_path = temp_image.name
        
        # Process the image and get the detected season
        undertone, iris_color, hair_color, skin_color, season = process_image(temp_image_path)
        
        # Delete the temporary file
        import os
        os.unlink(temp_image_path)
        
        # Get suggested colors for the detected season
        suggested_colors = get_suggested_colors(season)
        
        return {
            "season": season, 
            "undertone": undertone,
            "iris_color": iris_color,
            "hair_color": hair_color,
            "skin_color": skin_color,
            "suggested_colors": suggested_colors
        }
    
    class Input(BaseModel):
        file: UploadFile = File(...)
        
class detect_season_from_image_openai(BaseModel):
    async def process(self, file: UploadFile):
        processed_image = await preprocess_image(file)
        payload = create_payload(processed_image,prompts_by_section["runner"])
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        attributes = json.loads(response.json()["choices"][0]["message"]["content"])
        usage = response.json()["usage"]
        season = attributes["season"]
        season_colors = get_suggested_colors(season)
        attributes["season_colors"] = season_colors
        return {"response": attributes, "usage": usage}
    
    class Input(BaseModel):
        file: UploadFile = File(...)
        
class detect_season_with_selections(BaseModel):
    async def process(self, data: dict=Body(...)):
        undertone = data.get("undertone")
        iris_color = data.get("iris_color")
        hair_color = data.get("hair_color")
        skin_color = data.get("skin_color")

        print("chosen undertone: ", undertone)
        print("chosen iris color: ", iris_color)
        print("chosen hair color: ", hair_color)
        print("chosen skin color: ", skin_color)
        
        season = define_season(undertone, iris_color, hair_color, skin_color)
        return {"season": season}
    
    class Input(BaseModel):
        file: UploadFile = File(...)