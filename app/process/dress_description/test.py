
import PIL.Image
from .functions import create_payload,preprocess_image
import requests
import PIL
import os
file = PIL.Image.open(r"C:\Users\punee\OneDrive\Desktop\schematic.jpg")
processed_image = preprocess_image(file)
payload = create_payload(processed_image,"In the given circuit, what are the sub circuits / components? Also, list all the components shown in the sub circuit.")
api_key = os.getenv("OPENAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
response = requests.post(
    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
# description = response.json()["choices"][0]["message"]["content"]
print(response)
