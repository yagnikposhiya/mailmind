"""
author: Yagnik Poshiya
github: @yagnikposhiya

Generates a professional customer support reply email using OpenAI GPT model
based on the categorized email type, extracted customer info, and
RAG-retrieved documents from company knowledge base.
"""

import os
import json

from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv
from utils.utils import load_config
from rag.semantic_search import retrieve_relevant_context

load_dotenv() # load environment variable from .env file
config = load_config() # load project configuration

client = OpenAI(
    base_url=config["api_endpoint"]["openrouter"],
    api_key=os.getenv("OPENROUTER_API_KEY") if config["flags"]["credentials_from_env"] else "<api_key>"
)

def generate_reply_mail(category:str, extracted_info: dict) -> str:
    """
    Generates a personalized reply email using an LLM based on the email category,
    structured extracted info, and relevant document chunks (via RAG).

    Args:
        - category (str): One of "Inquiry", "Complaint", "Feedback", "Other".
        - extracted_info (dict): Structured data extracted from the customer's email.

    Returns:
        - str: Generated reply content to be sent to the customer.
    """

    # retrieve relevant context chunks from RAG
    context_chunks = retrieve_relevant_context(json.dumps(extracted_info, indent=2))
    context = "\n".join(context_chunks)

    # construct the prompt
    prompt = f"""
You are a customer support assistant for a jewellery manufacturing company named Tvisi Jewels Private Limited.

You are responding to a customer email that falls under the category: **{category}**.

Below is the structured information extracted from the customer's email:
{extracted_info}

Here is the relevant company information retrieved from internal documents:
{context}

Using the information above:
- Write a professional and helpful email to the customer.
- Be concise and respectful.
- Include relevant details like order status, product name, or resolution steps if available.
- Maintain a polite and reassuring tone.

Do not write email subject. And write "Tvisi Jewels Team" only at the end of the email.

Respond with only the email content. Do not mention that you are an AI. Write as if you are a real customer support representative of Tvisi Jewels.
"""
    
    try:
        # generate reply using LLM
        response = client.chat.completions.create(
            model=config["chat_completion_model"]["openrouter"],
            messages=[{"role":"user", "content":prompt}],
            temperature=0.7,
            max_tokens=300
        )

        # extract and return clean reply
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error generating reply: {e}")
        return "We are currently experiencing technical difficulties. Please expect a response shortly."
