import re


import re


# ===========================================
# Sender Cleaner
# ===========================================

def clean_sender(sender):

    if sender == "Not Detected":
        return sender

    sender = sender.strip()

    # Remove UPI IDs
    sender = re.sub(
        r'[A-Za-z0-9._%-]+@(?:okicici|okaxis|oksbi|ybl|ibl|paytm|okhdfcbank|axl)',
        '',
        sender,
        flags=re.IGNORECASE
    )

    # Stop at unwanted keywords
    sender = re.split(
        r'google|phonepe|pay|upi|transaction|reference|bank|indian bank|federal bank|axis bank|icici bank|hdfc bank|\(',
        sender,
        flags=re.IGNORECASE
    )[0]

    # Remove numbers
    sender = re.sub(r'\d+', ' ', sender)

    # Remove special characters
    sender = re.sub(r'[^A-Za-z ]', ' ', sender)

    # Remove duplicate spaces
    sender = re.sub(r'\s+', ' ', sender).strip()

    # Remove duplicate consecutive words
    words = []
    for word in sender.split():

        if word.lower() not in [w.lower() for w in words]:
            words.append(word)

    sender = " ".join(words)

    return sender.title()
import re

import re


# ===========================================
# UPI Cleaner
# ===========================================

def clean_upi(upi):

    if upi == "Not Detected":
        return upi

    upi = upi.lower()

    upi = upi.replace(" ", "")

    upi = upi.replace("(@", "@")

    upi = upi.replace("@@", "@")

    # Keep only valid characters
    upi = re.sub(
        r'[^a-z0-9@._-]',
        '',
        upi
    )

    # Remove multiple @
    if upi.count("@") > 1:

        first = upi.find("@")

        upi = upi[:first + 1] + upi[first + 1:].replace("@", "")

    return upi
import re


# ===========================================
# Transaction ID Cleaner
# ===========================================

def clean_transaction_id(txn):

    if txn == "Not Detected":
        return txn

    txn = re.sub(
        r'[^A-Za-z0-9]',
        '',
        txn
    )

    return txn.strip()