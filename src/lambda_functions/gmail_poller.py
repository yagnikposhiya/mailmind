"""
author: Yagnik Poshiya
github: @yagnikposhiya

Periodically polls the Gmail inbox using IMAP to check for new unread emails.
"""

from utils.gmail_utils import fetch_unread_emails
from storage.dynamodb_handler import store_email_log

emails = fetch_unread_emails() # call the function to get a list of unread emails (each as a dictionary

# iterate through each mail and display its details
for mail in emails:
    # print(f"From_name: {mail['from_name']}")
    # print(f"From_email: {mail['from_email']}")
    # print(f"To: {mail['to']}")
    # print(f"Date: {mail['date']}")
    # print(f"Time: {mail['time']}")
    # print(f"Subject: {mail['subject']}")
    # print(f"Body:\n{mail['body']}")

    store_email_log(mail) # save email metadata with body content
    print(f"Stored email from: {mail['from_email']}")