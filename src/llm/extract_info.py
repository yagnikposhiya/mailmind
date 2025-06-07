"""
author: Yagnik Poshiya
github: @yagnikposhiya

Uses OpenAI (via OpenRouter) to extract relevant information fields dynamically from a customer email.
"""

import os
import json

from openai import OpenAI
from dotenv import load_dotenv
from utils.utils import load_config

load_dotenv() # load environment variables from .env file
config = load_config() # load project configuration

# intialize OpenAI client via OpenRouter
client = OpenAI(
    base_url=config["api_endpoint"]["openrouter"], # default server for OpenRouter API
    api_key=os.getenv("OPENROUTER_API_KEY" if config["flags"]["credentials_from_env"] else "<api_key>")
)

def extract_email_info(subject:str, body:str) -> dict:
    """
    Extracts dynamic key-value fields from a customer email using LLM.

    Args:
        - subject (str): Email subject
        - body (str): Email body

    Returns:
        - dict: Extracted structured information in key-valueb pairs
    """

    # define system role for LLM behavior and output expectations
    system_prompt = """
You are a smart email parser for a jewellery manufacturing company's (Tvisi Jewels Private Limited) customer support system.

Your task is to extract all key-value pairs of relevant information from the email content.

- Return the output as valid JSON.
- The keys should reflect actual topics mentioned in the email (e.g. "product", "order_date", "customization_requested", "requested_action", and etc.)
- Do not invent or guess missing information.
- If the customer's name, customer's id, order id, and anything relevant is found in signature, extract it.
- Use lowercase snake_case for all keys.
- Do not include irrelevant fields or empty values.
"""
    user_prompt = f"""
Subject: {subject}
Body: {body}
"""

    # compose the message in chat format
    messages = [
        {"role":"system", "content":system_prompt},
        {"role":"user", "content":user_prompt}
    ]

    try:
        # send request to OpenRouter API
        response = client.chat.completions.create(
            model=config["chat_completion_model"]["openrouter"],
            messages=messages,
            temperature=0.0,
            max_tokens=300
        )

        # extract JSON content from LLM's response
        content = response.choices[0].message.content.strip() # strip() removes leading and trailing whitespaces from a string

        # parse valid json (safe guards)
        return json.loads(content)
    
    except Exception as e:
        print(f"Error extracting email info: {e}")
        return {}