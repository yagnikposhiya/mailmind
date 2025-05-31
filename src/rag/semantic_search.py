"""
author: Yagnik Poshiya
github: @yagnikposhiya

Performs semantic search using a FAISS index and retrieves relevant context
based on an input query for retrieval-augmented generation (RAG).
"""

import os
import json
import faiss
import numpy as np

from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() # load environment variables from .env file

# load OpenAI API key for embedding
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def embed_query(query:str) -> np.ndarray:
    """
    Embeds a single query using OpenAI embeddings.

    Args:
        - query (str): Natural language input from user/email.

    Returns:
        - np.ndarray: Embedding vector in float32 format.
    """

    response = client.embeddings.create(
        model = "text-embedding-3-small",
        input = [query]
    )

    embedding = response.data[0].embedding
    return np.array(embedding).astype("float32").reshape(1,-1)

def retrieve_relevant_context(query:str, top_k:int=5) -> List[str]:
    """
    Loads FAISS index and metadata, performs similarity search, and
    retrieves top-k relevant chunks for a given query.

    Args:
        - query (str): Customer's question or issue in text form
        - top_k (int): Number of top relevant chunks to return

    Returns:
        - List[str]: List of top-k most relevant knowledge base chunks.
    """

    # loads FAISS index from disk
    index = faiss.read_index("rag_index.faiss")

    # load associated chunk texts and metadata
    with open("rag_chunks.json","r") as f:
        data = json.load(f)
        chunks = data["chunks"]
        meta = data["meta"]
    
    # embed the query
    query_vector = embed_query(query)

    # perform similarity search
    distances, indices = index.search(query_vector, top_k)

    # extract matching chunks
    results = [chunks[i] for i in indices[0]]

    return results