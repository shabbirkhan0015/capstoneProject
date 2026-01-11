"""Vector store implementation using ChromaDB for RAG."""
import os
import sys
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config


class VectorStore:
    """Manages vector store for RAG retrieval."""
    
    def __init__(self):
        """Initialize vector store with embeddings."""
        self.embeddings = OpenAIEmbeddings(
            model=config.Config.EMBEDDING_MODEL,
            openai_api_key=config.Config.OPENAI_API_KEY
        )
        self.persist_directory = config.Config.CHROMA_PERSIST_DIR
        self.collection_name = config.Config.COLLECTION_NAME
        
        # Ensure persist directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.vectorstore = None
        self._initialize_store()
    
    def _initialize_store(self):
        """Initialize or load existing vector store."""
        try:
            # Try to load existing vector store
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings,
                collection_name=self.collection_name
            )
            # Check if collection has documents
            if self.vectorstore._collection.count() == 0:
                self._build_knowledge_base()
        except Exception as e:
            print(f"Initializing new vector store: {e}")
            self._build_knowledge_base()
    
    def _build_knowledge_base(self):
        """Build knowledge base from markdown files."""
        print("Building knowledge base from documents...")
        
        # Load documents from knowledge base directory
        loader = DirectoryLoader(
            config.Config.KNOWLEDGE_BASE_DIR,
            glob="**/*.md",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'}
        )
        documents = loader.load()
        
        if not documents:
            print("Warning: No documents found in knowledge base directory")
            return
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"Created {len(chunks)} document chunks")
        
        # Create vector store from chunks
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )
        
        print(f"Knowledge base built with {len(chunks)} chunks")
    
    def search(self, query: str, k: int = None) -> list:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            k: Number of results to return (defaults to config value)
        
        Returns:
            List of relevant document chunks with metadata
        """
        if k is None:
            k = config.Config.TOP_K_RESULTS
        
        try:
            # Perform similarity search
            results = self.vectorstore.similarity_search_with_score(
                query, k=k
            )
            
            # Filter by similarity threshold
            filtered_results = [
                {
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                }
                for doc, score in results
                if score <= (1 - config.Config.SIMILARITY_THRESHOLD)
            ]
            
            return filtered_results
        except Exception as e:
            print(f"Error during search: {e}")
            return []
    
    def get_relevant_context(self, query: str) -> str:
        """
        Get formatted context string from search results.
        
        Args:
            query: Search query
        
        Returns:
            Formatted context string
        """
        results = self.search(query)
        
        if not results:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Document {i}]\n{result['content']}\n"
            )
        
        return "\n".join(context_parts)

