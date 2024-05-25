import os
import tempfile
from fastapi import HTTPException

from core.common_modules.image_tools import encode_image, resize_image

def create_payload(base64_image,prompt):
    return {
        "model": "gpt-4-turbo-2024-04-09",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300,
    }
    
async def preprocess_image(file):
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400, detail="File must be a JPEG or PNG image")

    # Save the image to a temporary file
    contents = await file.read()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp:
        temp.write(contents)
        image_path = temp.name  # Get the path to the temporary file

    # Process the image
    resize_image(image_path)
    base64_image = encode_image(image_path)

    # Delete the temporary file
    os.remove(image_path)
    return base64_image