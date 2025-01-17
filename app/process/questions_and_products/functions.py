import os

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch
import requests



def create_payload(prompts_dict,queries,questions_n, gender_female):
    gender_string=""
    if gender_female:
        gender_string="The user's gender is female"
    else:
        gender_string="The user's gender is male"
    query = """{0} {1} {2}. {3}. Give {4} questions in the array.""".format(prompts_dict["context"]," ".join(queries),prompts_dict["runner"],gender_string,questions_n)
    return {
        "model": "gpt-3.5-turbo",
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

def get_questions(prompts_dict,queries,questions_n,gender_female):
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    questions = []
    payload = create_payload(prompts_dict,queries,questions_n,gender_female)
    response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    questions_string=response.json()["choices"][0]["message"]["content"]
    print(questions_string)
    questions=questions_string.replace("[","").replace("]","").replace("\n","")
    return questions.split(",")

def get_products(queries,products_n,gender_female):
    try:
        host = 'https://search-cocoproductsearch-b26gqvdt6jzgl4npxobu5itiaq.aos.eu-north-1.on.aws'
        if(gender_female):
            index_name = 'fashion_womens_products'
        else:
            index_name='fashion_mens_products'
        username = 'cocosearchuser'
        password = 'Puneet@32'
        openai_api_key = ""  # Secure password input
        url = f"{host}/{index_name}/_search/"
        vector_field = 'vector_field'  # Make sure this matches your index
        text_field = 'product_name'

        # 1. Embeddings: OpenAI for generating embeddings (if needed for re-embedding)
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)

        # 2. Vector Store: OpenSearchVectorSearch to connect to your index
        vector_store = OpenSearchVectorSearch(
            opensearch_url=host,
            index_name=index_name,
            embedding_function=embeddings,  
            http_auth=(username, password) if username and password else None,
            verify_certs=False,  # Only for testing/development if using self-signed certs
            search_type = "script_scoring",
            space_type = "cosinesimil",
            vector_field=vector_field,
            text_field=text_field
        )
        products_list=[]
        print(queries)
        queries.pop(0)
        print("queries for opensearch: ",queries)
        # --- Search Loop ---
        for query in queries:
            print(query)
            docs = vector_store.similarity_search(
                query,
                k=products_n,
                search_type="script_scoring",
                space_type="cosinesimil",
                vector_field=vector_field,
                text_field=text_field,
                metadata_field="poduct_attributes",
                filter_selector=["product_name"])  # k=3 by default (top 3 documents)
            filtered_docs = []
            for doc in docs:
                filtered_docs.append({
                    "ProductName": doc.metadata["product_name"],
                    "Brand": doc.metadata["brand"],
                    "Image": doc.metadata["imageURL"],
                    "Buy": doc.metadata["productURL"],
                })
            products_list.append({"products":filtered_docs})
        return products_list
    except Exception as e:
        print(e)

def get_q_and_p(prompts_dict, queries, products_n, questions_n, gender_female):
    questions= get_questions(prompts_dict,queries["chat_history"],questions_n, gender_female)
    products = get_products(queries["chat_history"],products_n, gender_female)
    return{"questions":questions,"products":products}
    