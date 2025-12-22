import os
from typing import List, Dict
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Use a local embedding model to avoid API key requirements for this MVP
Settings.embedding_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

_index = None

def build_sample_index(data_dir: str = "data"):
    """
    Loads documents from the data directory and builds a simple vector index.
    """
    global _index
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        # If empty, we might want to warn, but for now we assume data exists as per plan
    
    documents = SimpleDirectoryReader(data_dir).load_data()
    _index = VectorStoreIndex.from_documents(documents)
    print(f"Index built with {len(documents)} documents.")

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
