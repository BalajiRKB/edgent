import os
from typing import List, Dict
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

# Use a local embedding model to avoid API key requirements for this MVP
Settings.embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

_index = None
_chroma_client = None

def get_chroma_client():
    """Get or create the ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = int(os.getenv("CHROMA_PORT", "8000"))
        _chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
    return _chroma_client

def build_sample_index(data_dir: str = "data", force_reload: bool = False):
    """
    Loads documents from the data directory and builds a vector index in ChromaDB.
    If the collection already exists and has data, skips reloading unless force_reload=True.
    """
    global _index
    
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    # Connect to ChromaDB
    chroma_client = get_chroma_client()
    collection_name = "learning_resources"
    
    # Get or create collection
    chroma_collection = chroma_client.get_or_create_collection(collection_name)
    
    # Check if collection already has documents
    if chroma_collection.count() > 0 and not force_reload:
        print(f"ChromaDB collection '{collection_name}' already has {chroma_collection.count()} documents. Skipping reload.")
        # Just create the index from existing collection
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        _index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
        return
    
    # Load documents and build index
    documents = SimpleDirectoryReader(data_dir).load_data()
    
    # Create vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Build index
    _index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print(f"Index built with {len(documents)} documents and stored in ChromaDB.")

def query_resources(goal: str) -> List[Dict[str, str]]:
    """
    Queries the index for the given goal and returns top 3 resources.
    """
    global _index
    if _index is None:
        build_sample_index()
    
    query_engine = _index.as_query_engine(similarity_top_k=3)
    response = query_engine.query(f"What are the key concepts and resources for learning {goal}?")
    
    # Extract source nodes to get "titles" or snippets
    results = []
    for node in response.source_nodes:
        # In a real app, we'd parse metadata better. 
        # Here we just take a snippet of the text.
        content_preview = node.node.get_content()[:200].replace("\n", " ")
        results.append({
            "title": f"Resource from {node.node.metadata.get('file_name', 'doc')}",
            "snippet": content_preview + "..."
        })
        
    return results
