# Base Image:
FROM python:3.11.9

# Set Working Directory (to your project root):
WORKDIR /code 

# Copy project files (maintaining your folder structure):
COPY . . 

# Install dependencies:
RUN pip install --no-cache-dir -r requirements.txt

# Set Environment Variables:
ENV PYTHONUNBUFFERED=1

# Expose the port:
EXPOSE 8000  

# Command to run your application (now from the project root):
CMD ["python", "main.py"] 