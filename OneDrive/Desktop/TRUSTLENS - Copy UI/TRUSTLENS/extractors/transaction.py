import re
from extractors.cleaner import clean_transaction_id


def extract_transaction_id(ocr_result):

    transaction_id = "Not Detected"

    keywords = [

        "transaction id",
        "upi transaction id",
        "upi tansaction id",
        "google transaction id",
        "phonepe transaction id",
        "reference id",
        "reference number",
        "txn id",
        "utr"

    ]

    for i, line in enumerate(ocr_result):

        text = line.lower()

        if any(keyword in text for keyword in keywords):

            for j in range(i + 1, min(i + 4, len(ocr_result))):

                candidate = re.sub(
                    r'[^A-Za-z0-9]',
                    '',
                    ocr_result[j]
                )

                if len(candidate) >= 8:

                    transaction_id = candidate
                    break

            if transaction_id != "Not Detected":
                break

    transaction_id = clean_transaction_id(transaction_id)

    return transaction_id