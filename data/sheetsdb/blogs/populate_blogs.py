from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.callbacks import get_openai_callback
import os 
import shutil
import dotenv
import pandas as pd
dotenv.load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
def load_blogs_to_chromadb():
    sheet_id = "16_PW7w9yfvDSjoAvWtznwWYHr1PNUqCRbIb7W1g8EH4"
    r = "https://docs.google.com/spreadsheets/export?id={}&exportFormat=csv".format(sheet_id)
    print("blogs sheet loaded")
    df = pd.read_csv(r)
    n = 2
    urls = df.iloc[:n, 0].to_numpy()
    descriptions = df.iloc[:n, 1].to_numpy()
    print("Loading blogs from URLs")

    # Load the URLs into documents
    loader = UnstructuredURLLoader(urls=urls)
    documents = loader.load()
    print("Total Blogs Loaded: ",len(documents))

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    # Create embeddings
    embeddings = OpenAIEmbeddings()

    # Create and store the vector store
    persist_directory = './chromadb'
    
    # Delete the existing directory if it exists
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
    
    print("Getting Embeddings from OpenAI")
    with get_openai_callback() as cb:
        vectorstore = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)
        print(cb)
        
load_blogs_to_chromadb()