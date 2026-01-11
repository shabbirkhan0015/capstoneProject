"""Configuration settings for the E-Commerce Customer Support Assistant."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo-preview")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Vector Store Configuration
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/vectorstore")
    COLLECTION_NAME = "ecommerce_knowledge_base"
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Default to False for production
    PORT = int(os.getenv("PORT", 5001))
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "")  # Should be set in production
    
    # RAG Configuration
    TOP_K_RESULTS = 3
    SIMILARITY_THRESHOLD = 0.7
    
    # Knowledge Base Paths
    KNOWLEDGE_BASE_DIR = "./data/knowledge_base"
    
    # Tool Configuration
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30

