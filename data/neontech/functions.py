import os
import json
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the connection string from the environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create a connection pool

def format_json_as_paragraph(data, depth=0):
    
    paragraph = ""
    indent = "  " * depth  # Indentation based on depth

    if isinstance(data, dict):
        for key, value in data.items():
            paragraph += f"{indent}{key.capitalize()}: "

            if isinstance(value, (dict, list)):  
                # Recursive call for nested dictionaries/lists
                paragraph += format_json_as_paragraph(value, depth + 1) + "\n"  
            elif isinstance(value, list) and all(isinstance(item, str) for item in value):
                # Special handling for lists of strings
                paragraph += ", ".join(value) + "\n"
            else:
                paragraph += str(value) + "\n"
    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, (dict, list)):
                paragraph += f"{indent}- Item {index + 1}:\n"
                paragraph += format_json_as_paragraph(item, depth + 1) + "\n"  # Recursive call
            else:
                paragraph += f"{indent}- {item}\n"

    return paragraph.strip()  # Remove trailing newline

# Function to retrieve and process cocodata by ID
def get_cocodata_by_id(id):
    connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)
    data_json_string = ""
    with connection_pool.getconn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM \"User_Meta\" WHERE id = %s", (id,))
            result = cur.fetchone()

            if result:
                # Convert to regular dictionary 
                data = dict(result)

                # Drop unwanted keys
                for key in ['id', 'seasonColors']:
                    data.pop(key, None)  

                # Add 'gender' key based on 'genderFemale'
                if 'genderFemale' in data:
                    data['gender'] = 'female' if data['genderFemale'] else 'male'
                    del data['genderFemale'] 
                
                # Add 'cm' to height
                if 'height' in data:
                    data['height'] = str(data['height']) + ' cm'

                data_json_string = json.dumps(data)  # Serialize to JSON string
                
            else:
                return None
            
    # Close all connections in the pool
    connection_pool.closeall()
    
    return data_json_string


def get_metas_from_neon(user_id):

    # Fetch and process the cocodata
    cocodata_json_string = get_cocodata_by_id(user_id)

    if cocodata_json_string:
        cocodata = json.loads(cocodata_json_string)  
        formatted_output = format_json_as_paragraph(cocodata)
        return formatted_output
        
    else:
        print("Cocodata not found for the given ID.")
        return None

    