from PIL import Image
import base64
def resize_image(image_path, max_dimension=1024):
    with Image.open(image_path) as img:
        width, height = img.size
        if width > max_dimension or height > max_dimension:
            # Calculate new dimensions while maintaining aspect ratio
            if width > height:
                new_width = max_dimension
                new_height = int(height * (max_dimension / width))
            else:
                new_height = max_dimension
                new_width = int(width * (max_dimension / height))

            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            # Save the resized image (optional, depending on your needs)
            img.save(image_path)

# Function to encode the image


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')