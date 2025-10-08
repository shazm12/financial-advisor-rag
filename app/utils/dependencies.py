from app.utils.create_embeddings import CreateEmbeddings
from app.utils.document_extractor import DocumentExtractor
from app.utils.redisdb import RedisDB
from app.utils.retreiver import Retreiver
from app.utils.session_manager import SessionManager
from dotenv import load_dotenv
import os

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")

def get_document_extractor() -> DocumentExtractor:
    return DocumentExtractor()

def get_embedding() -> CreateEmbeddings:
    return CreateEmbeddings()

def get_session_manager() -> SessionManager:
    return SessionManager()

def get_redis_db() -> RedisDB:
    return RedisDB(redis_url=REDIS_URL)

def get_retreiver_class():
    return Retreiver
