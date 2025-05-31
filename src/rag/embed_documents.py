"""
author: Yagnik Poshiya
github: @yagnikposhiya

Loads documents from S3, chunks them, creates embeddings using OpenAI, 
and stores them in a FAISS (Facebook AI Similarity Search) index for semantic retrieval.
"""

"""
FAISS:
Facebook AI Similarity Search is a library that allows developers to quickly search for embeddings
of multimedia documents that are similar to each other.

Semantic Search & Retrieval Flow:
1. Load required documents from the S3 bucket.
2. Chunk the retrieved content into manageable text segments.
3. Embed each chunk into vector representations.
4. Store the vectors and corresponding chunks in a vector database (e.g., FAISS, Chroma).
5. Implement semantic search to retrieve the most relevant chunks for a given query.
"""

import os
import uuid
import faiss
import json
import numpy as np

from typing import Any
from openai import OpenAI
from dotenv import load_dotenv
from storage.s3_handler import read_all_documents_from_s3

load_dotenv() # load environment variables from .env file

# initialize OpenAI cliet with OpenRouter base_url
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def chunk_text(text:str, max_length:int=500) -> list:
    """
    Splits long text into smaller chunks based on max character length for embedding and semantic search.

    Args:
        - text (str): The full input text to be chunked.
        - max_length (int): The maximum number of characters per chunk. Default is 500.

    Returns:
        - list: A list of text chunks (strings), each not exceeding 'max_length' characters.
    """

    paragraphs = text.split("\n") # split input text into paragraphs using newline as delimeter
    chunks, current_chunk = [], "" # initialize the list to hold final chunks and a temporary chunk holder

    # iterate over each paragraph to construct chunks
    for para in paragraphs:
        if len(current_chunk) + len(para) < max_length: # if adding this paragraph keeps total chunk length under limit, append it
            current_chunk += para + "\n"
        else: # otherwise, save the current chunk and start a new one
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n"

    # add any remaining text as the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def embed_chunks_openai(chunks: list) -> np.ndarray:
    """
    Embeds a list of text chunks using OpenAI embedding model.

    Args:
        - chunks (list): List of text strings.

    Returns:
        - np.ndarray: Embedding vectors (numpy array)
    """

    # send all chunks to OpenAI embedding API for vector representation
    response = client.embeddings.create(
        model = "text-embedding-3-small", # e.g. text-embedding-3-small
        input=chunks
    )

    # extract embedding vectors from API response
    embeddings = [item.embedding for item in response.data]

    # convert the list of embeddings to a NumPy array with float32 precision
    return np.array(embeddings).astype("float32")

def build_faiss_index() -> Any:
    """
    Loads all documents from S3, chunks them, generates embeddings using OpenAI,
    and stores the vectors into FAISS index with corresponding metadata.
    """

    print("Loading documents from S3")
    docs = read_all_documents_from_s3() # load .docx and .csv documents from the S3 bucket

    texts, metadata = [], [] # lists to hold chunks and their metadata

    # loop/walk through each document and break it into chunks
    for filename, content in docs.items():
        chunks = chunk_text(content) # chunk the document text
        for chunk in chunks:
            texts.append(chunk) # add chunk to the text list
            metadata.append({
                "filename": filename, # file where chunk came from
                "chunk_id": str(uuid.uuid4()) # unique ID for the chunk
            })

    print(f"Total chunks: {len(texts)}")

    # generate embeddings for all text chunks using OpenAI
    print("Embedding chunks with OpenAI...")
    embeddings = embed_chunks_openai(texts)

    # build a FAISS index from embeddings
    print("Building and saving FAISS index...")
    dim = embeddings.shape[1] # dimentionsality of embedding vectors
    index = faiss.IndexFlatL2(dim) # L2-based flat index
    index.add(embeddings) # add all embedding vectors to the index
    faiss.write_index(index, "rag_index.faiss") # save the index to disk

    # save the chunks and their metadata for later use (semantic search)
    with open("rag_chunks.json","w") as f:
        json.dump({"chunks": texts, "meta": metadata}, f, indent=2)

    print("Embedding pipeline completed.")