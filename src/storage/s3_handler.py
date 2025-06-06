"""
author: Yagnik Poshiya
github: @yagnikposhiya

Reads all .docx and .csv documents from an s3 bucket or a folder within it.
Used for dynamically preparing text corpus for semantic search (RAG).
"""

import os
import csv
import boto3

from docx import Document # for parsing word documents
from dotenv import load_dotenv
from io import BytesIO, StringIO
from utils.utils import convert_csv_to_chunks

load_dotenv() # load environment variables from .env file

# initialize s3 client using credentials from environment
s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")

def read_all_documents_from_s3(prefix:str="") -> dict:
    """
    Reads all .docx and .csv files from an S3 bucket or a specified folder prefix.

    Args:
        - prefix (str): Optional prefix (folder path) in the bucket.

    Returns:
        - dict: A dictionary of {filename (S3 key): plain text content}
    """

    result = {}

    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix) # list all files in the bucket or in the prefix path

    # walk/loop through each object in the bucket
    for item in response.get("Contents",[]):
        key = item['Key']

        # skip unsupported file types
        if not key.endswith((".docx", ".csv")):
            continue

        try:
            # get file content from S3
            obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
            file_stream = BytesIO(obj['Body'].read())

            # process .docx files
            if key.endswith(".docx"):
                doc = Document(file_stream)
                text = "\n".join([p.text for p in doc.paragraphs])

            # process .csv files
            elif key.endswith(".csv"):
                decoded = file_stream.read().decode("utf-8")
                chunks = convert_csv_to_chunks(decoded)
                text = "\n".join(chunks)

            # add processed content to result
            result[key] = text

        except Exception as e:
            print(f"Error reading {key}: {e}")

    return result