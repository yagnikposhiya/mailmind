"""
author: Yagnik Poshiya
github: @yagnikposhiya

Sends a reply email to a customer using Gmail's SMTP server.
Ensures the email appears in the same thread as the original message by setting proper headers.
"""

import os
import smtplib

from email.message import EmailMessage

def send_email_reply(to_address, subject, body, original_msg_id) -> None:
    """
    Sends a reply email using Gmail SMTP, referencing original message for threading.

    Args:
        - to_address (str): Customer's email address
        - subject (str): Subject for the reply (same as original or prefixed with "Re:")
        - body (str): Generated email content
        - orignal_msg_id (str): Message-ID of the original customer email (for threading)
    """

    # get sender address
    from_address = os.getenv("GMAIL_ADDRESS")

    # create an email message object
    msg = EmailMessage()

    # set the email subject with "Re:" prefix for reply context
    msg['Subject'] = f"Re: {subject}"

    # set the sender's email address
    msg['From'] = from_address

    # set the recipient's email address
    msg['To'] = to_address

    # ensure threading by including original Message-ID in these headers
    msg['In-Reply-To'] = original_msg_id
    msg['References'] = original_msg_id

    # set the plain-text content of the email
    msg.set_content(body)

    # connect securely to Gmail SMTP server and send the message
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_address, os.getenv("GMAIL_APP_PASSWORD")) # authenticate with app password
        smtp.send_message(msg) # send the composed email
