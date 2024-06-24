import csv
import json
import re
import logging
import requests
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import openai
import dotenv
dotenv.load_dotenv()
import os
api_key = os.getenv("OPENAI_API_KEY")

# --- Configuration ---
base_url = "https://www.myntra.com/"
product_categories = [
    "men-footwear",
    "mens-watches",
    "men-sports-wear",
    "men-accessories",
    "men-bags-backpacks",
    ]
headless = True  # Set to True for headless mode
csv_filename = "myntra_products.csv"
log_filename = "myntra_errors.log"
opensearch_host = 'https://search-cocoproductsearch-b26gqvdt6jzgl4npxobu5itiaq.aos.eu-north-1.on.aws'
opensearch_index = 'fashion_mens_products'  # New index name
opensearch_username = 'cocosearchuser'
opensearch_password = 'Puneet@32'
# --- Logging Setup ---
logging.basicConfig(filename=log_filename, level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

proxy_list = [  # Add your proxy IP addresses and ports here

    "50.223.239.177:80",
    "50.207.199.80:80",
    "47.74.152.29:8888",
    "35.185.196.38:3128",
    "50.168.72.116:80",
    "20.210.113.32:8123",
    "20.205.61.143:80",
    "20.235.159.154:80",
    "65.109.189.49:80",
    "194.219.134.234:80",
    # Add more proxies as needed
]



# --- Post-Processing Functions ---

color_keywords = [
    # Basic Colors
    "black", "white", "grey", "gray", "red", "orange", "yellow", "green", 
    "blue", "purple", "brown", "pink",

    # Extended Color Names
    "beige", "ivory", "cream", "tan", "khaki", "olive", "lime", 
    "teal", "aqua", "turquoise", "navy", "indigo", "violet", "lavender",
    "mauve", "fuchsia", "magenta", "maroon", "burgundy", "scarlet",
    "crimson", "coral", "salmon", "peach", "apricot", "amber", "gold", 
    "bronze", "copper", "silver",
   
    # Shades and Tints
    "light blue", "dark blue", "sky blue", "royal blue", "midnight blue",
    "light green", "dark green", "forest green", "emerald green", "sea green",
    "light yellow", "dark yellow", "golden yellow", "lemon yellow",
    "light red", "dark red", "ruby red", "fire red", "brick red",
    "light purple", "dark purple", "violet", "amethyst", "plum",
    "light pink", "dark pink", "rose pink", "hot pink", "blush pink",

    # Metallic Colors
    "gold", "silver", "bronze", "copper",

    # Other Colors
    "cyan", "magenta", "charcoal", "taupe", "azure", "chartreuse",
    "mustard", "sepia", "mahogany", "rust", "coral", "indigo"
]
def process_color(description):
    if description:
        description = description.lower()  # Convert to lowercase for case-insensitive matching

        # 1. Direct Keyword Match with Word Boundaries
        for keyword in color_keywords:
            if re.search(rf"\b{keyword}\b", description):  # Use word boundaries
                return keyword

        # 2. Color Names with Hyphens
        hyphenated_colors = re.findall(r"(\w+-\w+)", description)
        for color in hyphenated_colors:
            if any(kw in color for kw in color_keywords):
                return color

        # 3. Combined Color Descriptions
        combined_colors = re.findall(r"(\w+ and \w+)", description)
        for color_pair in combined_colors:
            if all(kw in color_pair for kw in color_keywords):
                return color_pair

        # 4. Handle "Solid" Colors
        if "solid" in description:
            for keyword in color_keywords:
                if re.search(rf"\b{keyword}\b", description):  # Use word boundaries
                    return keyword

    return None


def return_text(element):
    return element.text

def process_product_name(element):
    return element.text

def process_product_price(element):
    return element.text.replace("Rs. ", "")

def process_product_attributes(element):
    attributes = {}

    # Click "See More" if it exists
    try:
        see_more_button = WebDriverWait(element, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "index-showMoreText"))
        )
        see_more_button.click()
    except TimeoutException:
        pass  # Button not found or already expanded

    # Find all table containers (both before and after "See More")
    table_containers = element.find_elements(By.CLASS_NAME, "index-tableContainer")

    for container in table_containers:
        rows = container.find_elements(By.CLASS_NAME, "index-row")
        for row in rows:
            key_element = row.find_element(By.CLASS_NAME, "index-rowKey")
            value_element = row.find_element(By.CLASS_NAME, "index-rowValue")
            attributes[key_element.text] = value_element.text

    return attributes

def get_image_url_from_div(element):
    style = element.get_attribute("style")
    start_index = style.find("url(") + 4
    end_index = style.find(")", start_index)
    url = style[start_index:end_index]

    # Remove unwanted characters
    url = url.replace('\"', '')   # Remove \"

    return url 


def get_current_page_url(driver):
    return driver.current_url

def process_rating_count(element):
    if element:
        text_content = element.text
        rating_text = text_content.split()[0] 

        multiplier = 1
        if rating_text.endswith("k"):
            multiplier = 1000
            rating_text = rating_text[:-1] 

        try:
            rating_value = float(rating_text) * multiplier
            return int(rating_value)
        except ValueError:
            return 0  # Return 0 if conversion fails or invalid format
    return 0  # Return 0 if element is not found

def process_fit_type(element):
    if element:  # Check if element is found
        text_content = element.get_attribute("innerHTML")
        fit_type = text_content.split("<br>")[0].strip()  # Split at <br>, take first part
        return fit_type
    return None  # Return None if element not found

def process_sizes(element):
    if element:
        size_elements = element.find_elements(By.CLASS_NAME, "size-buttons-unified-size")
        sizes = []
        for size_element in size_elements:
            size_text = size_element.text
            size_text = size_text.split("\n")[0]  # Get only the first line (size)
            sizes.append(size_text)
        return sizes  # Return the list of sizes directly
    return None


def return_float(element):
    try:
        return float(element.text) if element else 0.0
    except ValueError:
        return 0.0

# --- Customizable Product Page Interface ---   
product_details = {
    "product_name": {
        "identifier": By.CLASS_NAME, "name": "pdp-name", "post_processing": return_text
    },
    "product_price": {
        "identifier": By.XPATH, "name": '//*[(@id = "mountRoot")]//strong', "post_processing": process_product_price
    },
    "avg_rating": {
        "identifier": By.CLASS_NAME, "name": "index-overallRating div:nth-child(1)", "post_processing": return_float
    },
    "brand": {
        "identifier": By.CLASS_NAME, "name": "pdp-title", "post_processing": return_text
    },
    "color": {
        "identifier": By.CLASS_NAME, "name": "pdp-productDescriptorsContainer div:nth-child(1) .pdp-product-description-content", "post_processing": lambda element: process_color(return_text(element)) 
    },
    "description": {
        "identifier": By.CLASS_NAME, "name": "pdp-productDescriptorsContainer div:nth-child(1) .pdp-product-description-content", "post_processing": return_text 
    },
    "imageURL": {
        "identifier": By.XPATH, "name": '//*[contains(concat( " ", @class, " " ), concat( " ", "image-grid-col50", " " )) and (((count(preceding-sibling::*) + 1) = 1) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "image-grid-image", " " ))]', "post_processing": get_image_url_from_div
    },
    "productURL": {
        "identifier": None, "name": None, "post_processing": get_current_page_url
    },
    "product_attributes": {
        "identifier": By.CLASS_NAME, "name": "index-sizeFitDesc", "post_processing": process_product_attributes
    },
    "product_id": {
        "identifier": By.CLASS_NAME, "name": 'supplier-styleId', "post_processing": return_text
    },
    "sizes": {
        "identifier": By.CLASS_NAME, "name": 'size-buttons-size-buttons', "post_processing": process_sizes
    },
    "rating_count": {
        "identifier": By.CLASS_NAME, "name": 'index-ratingsCount', "post_processing":process_rating_count
    },
    "fit_type": {
        "identifier": By.XPATH, "name": '//*[contains(concat( " ", @class, " " ), concat( " ", "pdp-sizeFitDesc", " " )) and (((count(preceding-sibling::*) + 1) = 2) and parent::*)]//*[contains(concat( " ", @class, " " ), concat( " ", "pdp-product-description-content", " " ))]', "post_processing": process_fit_type #TODO
    },
}


# --- Functions ---
def product_exists_in_index(product_id):
    search_url = f"{opensearch_host}/{opensearch_index}/_search"
    query = {"query": {"term": {"product_id": product_id}}}
    try:
        response = requests.get(search_url, json=query, auth=HTTPBasicAuth(opensearch_username, opensearch_password))
        response.raise_for_status()
        return response.json()['hits']['total']['value'] > 0
    except Exception as e:
        logging.error(f"Error checking product existence: {e}")
        return False
    
def scrape_product_page(driver, product_url):
    try:
        product_data = {}
        for field, details in product_details.items():
            if details["identifier"] is None: 
                product_data[field] = details["post_processing"](driver)  
            else:
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((details["identifier"], details["name"]))
                    )
                    product_data[field] = details["post_processing"](element)
                except StaleElementReferenceException:
                    element = driver.find_element(details["identifier"], details["name"])
                    product_data[field] = details["post_processing"](element)
                except (NoSuchElementException, TimeoutException):
                    logging.error(f"Error scraping field '{field}' on product: {product_url}")
                    product_data[field] = None 
        return product_data
    except Exception as e:  # Catch any unexpected errors
        logging.error(f"Unexpected error scraping product: {product_url} - {e}")
        return None  # Return None to indicate failure
    
def ingest_product(product_data):
    url = f"{opensearch_host}/{opensearch_index}/_doc/"
    client = openai.OpenAI(api_key=api_key) 

    # --- Generate Vector Embedding ---
    text_to_embed = product_data["product_name"] + " " + product_data.get("description", "") 
    vector_embedding = client.embeddings.create(
        input=text_to_embed, 
        model="text-embedding-ada-002"
    ).data[0].embedding

    product_data["vector_field"] = vector_embedding  # Add the vector to the product data
    
    # --- Ingest into OpenSearch ---
    try:
        response = requests.post(url, json=product_data, auth=HTTPBasicAuth(opensearch_username, opensearch_password))
        if response.status_code == 201:
            logging.info(f"Record with vector uploaded successfully: {response.json()['_id']}")
            print(f"Record with vector uploaded successfully: {response.json()['_id']}")
        else:
            logging.error(f"Failed to upload record: {response.status_code} - {response.text}")
            print(f"Failed to upload record: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Failed to upload record: {e}")
        print(f"Failed to upload record: {e}")



starting_page = 25

def scrape_category(driver, category, writer, proxy):
    if proxy:
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": proxy,
            "ftpProxy": proxy,
            "sslProxy": proxy,
            "proxyType": "MANUAL",
        }
    url = base_url + category
    driver.get(url)

    # Navigate to the starting page
    for _ in range(starting_page - 1):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pagination-next"))
            )
            driver.find_element(By.CLASS_NAME, "pagination-next").click()  # Find and click again
        except TimeoutException:
            print(f"Starting page {starting_page} not found or timeout occurred in category {category}.")
            return  # Skip this category if the starting page isn't found

    
    page_number = starting_page

    while True:
        print(f"Processing page {page_number} of category {category}")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "results-base"))
            )
            while True:  # Inner loop to handle stale element exceptions
                try:
                    product_links = [
                        product.find_element(By.TAG_NAME, "a").get_attribute("href")
                        for product in driver.find_elements(By.CLASS_NAME, "product-base")
                    ]
                    for link in product_links:
                        product_id = link.split("/")[-2]

                        if not product_exists_in_index(product_id):
                            print(f"Scraping and ingesting product: {link}")

                            # Use JavaScript to open the link in a new tab
                            driver.execute_script(f"window.open('{link}', '_blank');")
                            driver.switch_to.window(driver.window_handles[-1])  # Switch to new tab

                            product_data = scrape_product_page(driver, link)
                            if product_data:
                                ingest_product(product_data)

                            driver.close()  # Close the product tab
                            driver.switch_to.window(driver.window_handles[0])  # Switch back to main tab

                        else:
                            print(f"Skipping product (already in index): {link}")
                        print("link: ", link)
                    break  # Exit inner loop if successful
                except StaleElementReferenceException:
                    print("Stale element reference encountered. Retrying...")

            # Check for next page button and click
            next_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "pagination-next"))
            )
            if "disabled" in next_page.get_attribute("class"):
                break

            next_page.click()
            page_number += 1
            
            
        except TimeoutException:
            print("No more products found or timeout occurred.")
            break

# --- Main Scraping Logic ---
options = webdriver.ChromeOptions()
if headless:
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")

with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = product_details.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    # Proxy Rotation
    for category in product_categories:
        print(f"Scraping category: {category}")
        for proxy in proxy_list:
            try:
                driver = webdriver.Chrome(options=options)  # Create a new driver for each proxy
                scrape_category(driver, category, writer, proxy)
                driver.quit()  # Quit the driver after using each proxy
            except Exception as e:
                logging.error(f"Error with proxy {proxy}: {e}")

driver.quit()