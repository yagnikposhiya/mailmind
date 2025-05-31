"""
author: Yagnik Poshiya
github: @yagnikposhiya


"""

import pandas as pd
from io import StringIO

def convert_csv_to_chunks(decoded_csv:str) -> list:
    """
    Converts CSV content into semantically meaningful sentences for embedding.

    Args:
        - decoded_csv (str): CSV file content decoded as a UTF-8 string.

    Returns:
        - list: List of semantically meaningful text chunks, one per row
    """

    # read the CSV content into a DataFrame
    df = pd.read_csv(StringIO(decoded_csv))

    chunks = []

    # convert each row into a structured sentence
    for _, row in df.iterrows():
        # combine column names with their respective values
        sentence = ".".join(f"{col.strip()}: {str(row[col]).strip()}"
                            for col in df.columns if pd.notna(row[col])
                            )
        
        chunks.append(sentence)

    return chunks