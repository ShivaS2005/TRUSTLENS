import re

from extractors.googlepay import extract_google_amount
from extractors.phonepe import extract_phonepe_amount
from extractors.generic import extract_generic_amount


def extract_receipt_details(payment_app, ocr_result):

    details = {

        "amount": "Not Detected",
        "upi": "Not Detected",
        "transaction_id": "Not Detected",
        "date": "Not Detected",
        "time": "Not Detected"

    }

    # Amount
    if payment_app == "Google Pay":

        details["amount"] = extract_google_amount(ocr_result)

    elif payment_app == "PhonePe":

        details["amount"] = extract_phonepe_amount(ocr_result)

    else:

        details["amount"] = extract_generic_amount(ocr_result)

    return details