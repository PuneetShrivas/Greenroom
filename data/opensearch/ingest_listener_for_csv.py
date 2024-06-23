import csv
import json
import time
import logging
from requests.auth import HTTPBasicAuth
import pandas as pd
import requests


# --- Configuration ---
csv_filename = "myntra_products.csv"
host = 'https://search-cocoproductsearch-b26gqvdt6jzgl4npxobu5itiaq.aos.eu-north-1.on.aws'
index_name = 'fashion_index'
username = 'cocosearchuser'
password = 'Puneet@32'
polling_interval = 5  # Seconds

# --- Logging Setup ---
logging.basicConfig(filename="ingestion.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.getLogger('requests').setLevel(logging.WARNING)  # Lower logging level for requests library


# --- Functions ---
def product_exists_in_index(product_id):
    search_url = f"{host}/{index_name}/_search"
    query = {
        "query": {
            "term": {
                "product_id": product_id
            }
        }
    }
    try:
        response = requests.get(search_url, json=query, auth=HTTPBasicAuth(username, password))
        response.raise_for_status()  # Raise an exception if the request failed
        search_result = response.json()
        return search_result['hits']['total']['value'] > 0
    except Exception as e:
        logging.error(f"Error checking product existence: {e}")
        return False  # Assume the product doesn't exist if there's an error

def ingest_row(row):
    url = f"{host}/{index_name}/_doc/"
    if not product_exists_in_index(row["product_id"]):  # Check if product exists before inserting
        try:
            response = requests.post(url, json=row, auth=HTTPBasicAuth(username, password))
            if response.status_code == 201:
                logging.info(f"Record uploaded successfully: {response.json()['_id']}")
                print(f"Record uploaded successfully: {response.json()['_id']}")
            else:
                logging.error(f"Failed to upload record: {response.status_code} - {response.text}")
                print(f"Failed to upload record: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Failed to upload record: {e}")
            print(f"Failed to upload record: {e}")

# --- Main Loop ---
def main():
    processed_rows = set() 
    with open(csv_filename, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_str = json.dumps(row, sort_keys=True)
            if row_str not in processed_rows:
                ingest_row(row)
                processed_rows.add(row_str)

    # Continuously monitor the file for new rows
    last_line_number = sum(1 for line in open(csv_filename, "r", encoding="utf-8")) - 1 # minus header
    while True:
        current_line_number = sum(1 for line in open(csv_filename, "r", encoding="utf-8")) - 1
        if current_line_number > last_line_number:
            with open(csv_filename, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row_str = json.dumps(row, sort_keys=True)  
                    if row_str not in processed_rows:
                        ingest_row(row)
                        processed_rows.add(row_str)

            last_line_number = current_line_number  # Update last processed line number
        time.sleep(polling_interval) 

if __name__ == "__main__":
    main()
