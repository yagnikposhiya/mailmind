"""
author: Yagnik Poshiya
github: @yagnikposhiya

Authenticates and interfaces with Gmail's IMAP server for email access.
"""

import os
import email
import imaplib

from dotenv import load_dotenv
from typing import Any, List, Dict
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime

load_dotenv() # load environment variables from .env file

# Gmail credentials loaded from environment
GMAIL_USER = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

def connect_to_gmail() -> Any:
    """
    Establishes a secure connection to the Gmail IMAP server and logs in
    using credentials from the environment.

    Returns:
        - imaplib.IMAP4_SSL: Autheticated IMAP connection object.
    """

    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER,GMAIL_APP_PASSWORD)
    return imap

def decode_MIME_words(header_value:str) -> str:
    """
    Decodes MIME encoded-words (e.g.,  non-ASCII characters in Subject or Name headers).

    Args:
        - header_value (str): The raw email header string to decode.

    Returns:
        - str: A UTF-8 decoded header string.
    """

    if header_value is None:
        return ""
    
    decoded_parts = decode_header(header_value)

    return ''.join(
        part.decode(enc or "utf-8") if isinstance(part, bytes) else part
        for part, enc in decoded_parts
    )

def fetch_unread_emails() -> Any:
    """
    Fetches unread emails from Gmail inbox, extracts:
    fron_name, from_email, to, subject, date, time, body

    Returns:
        - List[Dict[str, str]]: A list of dictionaries, each containing one email's details.
    """

    imap=connect_to_gmail()
    imap.select("inbox") # select the inbox folder

    # search for all unread/unseen messages
    status, messages = imap.search(None,'(UNSEEN)')
    email_list = []

    if status != "OK"  or not messages[0]:
        print("No new emails found.")
        return []
    
    # loop through each unread email
    for num in messages[0].split():
        # fetch the full RFC822 message by its ID
        status, data = imap.fetch(num, "(RFC822)")
        if status != "OK":
            print("Failed to fetch email.")
            continue
        
        # parse raw bytes into an email message object
        msg = email.message_from_bytes(data[0][1])

        # decode the subject line
        subject = decode_MIME_words(msg["Subject"])

        # parse sender (From:)
        from_raw = msg.get("From")
        from_name, from_email = parseaddr(from_raw)

        # parse recipient (To:)
        to_raw = msg.get("To")
        to_name, to_email = parseaddr(to_raw) if to_raw else ("","")

        # Parse the date header and format into date/time strings
        date_header = msg.get("Date")
        if date_header:
            dt = parsedate_to_datetime(date_header)
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M:%S")
        else:
            date_str, time_str = "", ""

        # initialize email body
        body = ""

        # if the mail has multiple parts (e.g. plain text and HTML)
        if msg.is_multipart():
            # walk through the email parts and find plain text
            for part in msg.walk():
                # look for the plain text version
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset,errors="ignore")
                    break
        else:
            # if email has only one single part plain text
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        # append the extracted details to the list
        email_list.append({
            "from_name": from_name,
            "from_email": from_email,
            "to": to_email,
            "date": date_str,
            "time": time_str,
            "subject": subject,
            "body": body.strip()
        })

        # mark the email as read (seen)
        imap.store(num, "+FLAGS","\\Seen")

    # close the connection
    imap.logout()
    
    return email_list
