import requests
from requests.auth import HTTPBasicAuth
import json
import logging
from tqdm import tqdm
import openai
from dotenv import load_dotenv
import os
load_dotenv()

# Logging Setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# OpenSearch Credentials and Configuration
host = 'https://search-cocoproductsearch-b26gqvdt6jzgl4npxobu5itiaq.aos.eu-north-1.on.aws'
index_name = 'fashion_mens_products'
username = 'cocosearchuser'
password = 'Puneet@32'
url = f"{host}/{index_name}/_search?scroll=5m&size=1000"
auth = HTTPBasicAuth(username, password)

# OpenAI API Key (Replace with your actual key from the .env file)
openai_api_key = ""

def generate_embeddings(texts):
    # Creating an OpenAI client object with the api_key
    client = openai.OpenAI(api_key=openai_api_key) 
    return [client.embeddings.create(input=text, model="text-embedding-ada-002").data[0].embedding for text in texts] 


def update_document(doc_id, vector):
    update_url = f"{host}/{index_name}/_update/{doc_id}"
    headers = {'Content-Type': 'application/json'}
    payload = {"doc": {"vector_field": vector}}
    response = requests.post(update_url, auth=auth, headers=headers, data=json.dumps(payload))
    if not response.ok:
        logging.error(f"Failed to update document {doc_id}: {response.content}")


# 1. Update Mapping to Create the New Field (If it doesn't exist)
try:
    mapping_url = f"{host}/{index_name}/_mapping"
    response = requests.get(mapping_url, auth=auth)
    if not response.ok:
        raise Exception(f"Error getting mapping: {response.content}")

    current_mapping = response.json()[index_name]["mappings"]["properties"]
    if "vector_field" not in current_mapping:
        new_mapping = {
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 1536
                }
            }
        }
        response = requests.put(mapping_url, auth=auth, headers={'Content-Type': 'application/json'}, data=json.dumps(new_mapping))
        if not response.ok:
            raise Exception(f"Error updating mapping: {response.content}")
except Exception as e:
    logging.error(f"Error handling mapping: {e}")
    exit(1)  # Exit on mapping error

scroll_id = None
total_docs = 0
updated_docs = 0
with tqdm(desc="Processing Documents", unit="docs") as pbar:
    while True:
        if scroll_id:
            response = requests.post(f"{host}/_search/scroll", auth=auth, data=json.dumps({"scroll": "5m", "scroll_id": scroll_id}))
        else:
            response = requests.get(url, auth=auth)

        if not response.ok:
            logging.error(f"Error retrieving documents: {response.content}")
            break

        data = response.json()
        hits = data["hits"]["hits"]
        if not hits:
            break  # No more documents

        scroll_id = data["_scroll_id"]  # Update scroll ID
        total_docs += len(hits)

        for hit in hits:
            doc_id = hit["_id"]

            try:
                script_source = []
                if "product_vectors" in hit["_source"]:
                    script_source.append("ctx._source.remove('product_vectors');")
                if "vectorstore" in hit["_source"]:
                    script_source.append("ctx._source.remove('vectorstore');")

                # Add vector_field if not already present, or update existing one
                if "vector_field" not in hit["_source"]:
                    script_source.append("ctx._source.vector_field = params.vector;")

                if script_source:  # Only update if there's something to change
                    script = {
                        "source": "ctx._source.remove('product_vectors'); ctx._source.remove('vectorstore'); if (ctx._source.containsKey('vector_field') == false) { ctx._source.vector_field = params.vector; }",
                        "params": {
                            "vector": generate_embeddings([hit["_source"]["product_name"] + " " + hit["_source"]["description"]])[0]
                        }
                    }
                    update_url = f"{host}/{index_name}/_update/{doc_id}"
                    response = requests.post(update_url, auth=auth, headers={'Content-Type': 'application/json'}, json={"script": script})
                    if response.ok:
                        updated_docs += 1
                    else:
                        logging.error(f"Failed to update document {doc_id}: {response.content}")
            except Exception as e:
                logging.error(f"Error processing document {doc_id}: {e}")

            logging.info(f"Processed {total_docs} documents, updated {updated_docs} documents.")
            pbar.update(1)
print(f"Finished processing {total_docs} documents. Updated {updated_docs} documents.")
