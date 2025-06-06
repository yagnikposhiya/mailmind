"""
author: Yagnik Poshiya
github: @yagnikposhiya

Periodically polls the Gmail inbox using IMAP to check for new unread emails.
"""

from utils.send_mail import send_email_reply
from llm.extract_info import extract_email_info
from llm.categorize_email import categorize_email
from utils.gmail_utils import fetch_unread_emails
from storage.dynamodb_handler import store_email_log
from llm.generate_response import generate_reply_mail

emails = fetch_unread_emails() # call the function to get a list of unread emails (each as a dictionary

# iterate through each mail and display its details
if emails:
    for mail in emails:
        # print(f"From_name: {mail['from_name']}")
        # print(f"From_email: {mail['from_email']}")
        # print(f"To: {mail['to']}")
        # print(f"Date: {mail['date']}")
        # print(f"Time: {mail['time']}")
        # print(f"Subject: {mail['subject']}")
        # print(f"Body:\n{mail['body']}")

        category = categorize_email(mail['subject'],mail['body'])
        mail['category'] = category # append category to mail metadata and content dict
        print("Predicted category:", category)

        if category.lower() != "other": # if email is categorized in "other"; consider it spam email.

            extracted_info = extract_email_info(mail['subject'], mail['body'])
            mail['extracted_info'] = extracted_info # append extracted_info column to mail metadata and content dict
            print(f"Extracted information: {extracted_info}")

            reply_mail = generate_reply_mail(category, extracted_info) # generate a mail reply
            mail['email_reply'] = reply_mail
            print(f"Reply mail: {reply_mail}")

            send_email_reply(mail['from_email'], mail['subject'], reply_mail, mail['email_msg_id']) # send an email reply

            store_email_log(mail) # save email metadata with body content
            print(f"Stored email from: {mail['from_email']}")