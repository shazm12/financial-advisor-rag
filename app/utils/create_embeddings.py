import os
from langchain_community.vectorstores.redis import Redis
from langchain_community.embeddings import HuggingFaceEmbeddings  # Fixed import
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")


class CreateEmbeddings:

    def __init__(self):
        pass

    def create_embeddings_for_transactions_data(self, transactions_data):
        try:
            transaction_text_data = [
                t["text"] for t in transactions_data if "text" in t
            ]
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            rds = Redis.from_texts(
                texts=transaction_text_data,
                embedding=embeddings,
                redis_url=REDIS_URL,
                index_name="transactions_index",
            )
            return rds
        except Exception as e:
            print(f"Error Embedding and storing in vector DB: {e}")

    def create_embeddings_for_text_data(self, text_data):
        try:

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=len,
                is_separator_regex=False,
            )
            
            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )

            texts = text_splitter.split_text(text_data)
            
            rds = Redis.from_texts(
                texts=texts,
                embedding=embeddings,
                redis_url=REDIS_URL,
                index_name=f"full_text_index",
            )
            
            return rds

        except Exception as e:
            print(f"Error embedding and storing in vector DB: {e}")
            return None