import os
import pandas as pd
import csv
from openai import OpenAI
import requests
import tempfile
import mimetypes

client = OpenAI(api_key=openai_api_key)
from pprint import pprint
def transcribe(pathname):
    audio_file= open(pathname, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return(transcription.text)  
        
def get_rows(sheets_id,gid):
    sheet_link = "https://docs.google.com/spreadsheets/export?id={0}&gid={1}&exportFormat=csv".format(sheets_id,gid)
    print(sheet_link)
    df = pd.read_csv(sheet_link)
    print(df)
    return df


def download_and_transcribe(google_drive_link):
    file_id = google_drive_link.split("/")[-2]
    print("downloading audio")
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

    # with requests.get(download_url, stream=True) as response:
    #     response.raise_for_status()

    #     # Determine file type from content header (if available) or URL
    #     content_type = response.headers.get("Content-Type")
    #     if not content_type:  # Fallback to guessing from URL
    #         content_type, _ = mimetypes.guess_type(download_url)

    #     file_extension = mimetypes.guess_extension(content_type)
    #     if not file_extension:  # Default to a common format if unknown
    #         file_extension = ".mp3"

    #     with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             if chunk:
    #                 temp_file.write(chunk)

    #     print("file _saved: ", temp_file.name)
    transcription = transcribe(r"C:\Users\punee\Downloads\record-1719916182131.wav")

        # os.remove(temp_file.name) 

    return transcription

def create_payload(transcript,prompt,fields):

    query = """{0}
    {1}
    {2}
    Give No other text apart from the JSON.""".format(prompt,fields,transcript)
    return {
        "model": "gpt-4-turbo-2024-04-09",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query
                    }
                ]
            }
        ],
        "max_tokens": 2000,
    }

def process_row(audio_file_link, prompt, fields):
    transcript = download_and_transcribe(audio_file_link)
    payload = create_payload(transcript, prompt,fields)
    api_key = openai_api_key
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print(response)
    return response.json()["choices"][0]["message"]["content"]

sheets_id = "14TqbUDA3fOijNRQtPWeJEDgCf59adPIlpvmtQA6Sv2I"
gid = "2095715743"
prompt="""take the below transcript between me and a potential customer which i want to summarize in the following fields. Give the content as fields in the following JSON format:"""
fields="""[
    {{{{"customer background":"Information about the past experiences of the customer"
    }}}},
    {{{{"Problem Statement":"The major problem faced by the customer"
    }}}},
    {{{{"Top Problems":"Problem 1: <>, Problem 2: <>, Problem 3: <>,  Problem 4: <>, Problem 5: <>"
    }}}},
    {{{{"Current solutions":"How are they solving the problem presently"
    }}}},
    {{{{"Quantify resources":"Quantify resources & costs being used to solve currently"
    }}}},
    {{{{"Gaps":" Gaps in the current solution"
    }}}},
    {{{{"Improvements":"How can we change / Add value / How much "
    }}}},
    {{{{"Impact":"Who are the people most impacted"
    }}}},
    ]"""

print("downloading rows")
# rows=get_rows(sheets_id,gid)
rows = [{"audio_file":"https://drive.google.com/file/d/19rbmL7f92WYvxkXpUskyYOj6-_lTHA-K/view?usp=sharing"}]
for row in rows:
    print(row)
    audio_file_link=row["audio_file"]
    response_fields = process_row(audio_file_link, prompt, fields)
    print(response_fields)
    print("*****************************************************")
    
    

    

        