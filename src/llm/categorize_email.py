"""
author: Yagnik Poshiya
github: @yagnikposhiya

Uses OpenAI's GPT to classify a customer email into one of four categories:
Inquiry, Complaint, Suggestions/Feedback, or Other.
"""

import os

from openai import OpenAI
from dotenv import load_dotenv
from utils.utils import load_config

load_dotenv() # load environment variables from .env file
config = load_config() # load project configuration

# load OpenAI API key from environment
client = OpenAI(
    base_url=config["api_endpoint"]["openrouter"], # without this OpenAI SDK sends requests to a default server i.e. https://api.openai.com/v1; but given is the defualt server for OpenRouter
    api_key=os.getenv("OPENROUTER_API_KEY" if config["flags"]["credentials_from_env"] else "<api_key>")
    )

def categorize_email(subject:str, body:str) -> str:
    """
    Categorizes a customer email into: Inquiry, Complaint, Suggestions/Feedback, or Other.

    Args:
        - subject (str): The email subject.
        - body (str): The plain text email body.

    Returns:
        - str: One of the four categories.
    """

    context = """
You are an intelligent email classifier working for a customer support system of jewellery manufacturing company i.e. Tvisi Jewels Private Limited.

Only classify the email into the following categories if the content is related to jewellery, jewellery manufacturing, order issues, product feedback, or customer inquiries about jewellery:

1. Inquiry
2. Complaint
3. Feedback

If the email is **not relevant** to jewellery or your business domain (e.g. job applications, unrelated offers), then classify it strictly as:

4. Other

Respond with ONLY the category name even do not mention category index for example 1., 2., 3. ... (no explanation).
"""
    prompt = f"""
Subject: {subject}
Body: {body}
"""
    try:
        response = client.chat.completions.create(model=config["chat_completion_model"]["openrouter"],
        messages=[
            {"role":"system", "content":context}, # task instructions
            {"role":"user", "content":prompt} # content on which task should be performed with given instruction
        ],
        temperature=0.0, # 0.0 value make sure the model always returns consistent and controlled outputs, which is perfect for classification.
        # =0.0 > model always picks the most likely token, =1.0 > more randomness, variety in outputs, =>1.0 > high creativity, but potentially less reliable
        
        max_tokens=10) # max no. of tokens the model is allowed to generate in response. (1 token = 4 characters on average)

        category = response.choices[0].message.content.strip() # strip() removes leading and trailing whitespaces from a string
        return category

    except Exception as e:
        print(f"Error categorizing email: {e}")
        return "Other"