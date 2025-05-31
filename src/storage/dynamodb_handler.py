"""
author: Yagnik Poshiya
github: @yagnikposhiya

Performs read and write operations on DynamoDB for email metadata and logs.
"""

import os
import uuid
import boto3

from dotenv import load_dotenv

# load config
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
REGION = os.getenv("AWS_REGION")

# create dynamodb client
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

def store_email_log(email_data:dict) -> None:
    """
    Stores a sigle email entry in DynamoDB.

    Args:
        - email_data (dict): Dictionary containing email metadata
    """

    email_item = {
        "email_id": str(uuid.uuid4()),  # unique ID
        "email_msg_id": email_data.get("email_msg_id",""),
        "from_name": email_data.get("from_name", ""),
        "from_email": email_data.get("from_email", ""),
        "to": email_data.get("to", ""),
        "subject": email_data.get("subject", ""),
        "body": email_data.get("body", ""),
        "date": email_data.get("date", ""),
        "time": email_data.get("time", ""),
        "status": "received",
        "category": email_data.get("category",""),
        "extracted_info": email_data.get("extracted_info",""),
        "email_reply": email_data.get("email_reply","")
    }
    table.put_item(Item=email_item)