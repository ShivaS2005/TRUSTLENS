import re

def extract_bank(full_text, lines):

    bank = "Not Detected"

    bank_keywords = {
        "federal bank": "Federal Bank",
        "state bank": "State Bank of India",
        "sbi": "State Bank of India",
        "canara": "Canara Bank",
        "kvb": "Karur Vysya Bank",
        "karur vysya": "Karur Vysya Bank",
        "hdfc": "HDFC Bank",
        "icici": "ICICI Bank",
        "axis": "Axis Bank",
        "indian bank": "Indian Bank",
        "union bank": "Union Bank",
        "idfc": "IDFC First Bank",
        "yes bank": "Yes Bank",
        "kotak": "Kotak Mahindra Bank"
    }

    # Check known bank keywords
    for key, value in bank_keywords.items():

        if key in full_text.lower():

            return value

    # Fallback
    for line in lines:

        line_lower = line.lower().strip()

        if "@" in line_lower:
            continue

        if "transaction" in line_lower:
            continue

        if "bank" in line_lower:

            return line.title()

    return bank
def extract_phonepe_bank(ocr_result):

    bank = "Not Detected"

    bank_keywords = {

        "kvb": "Karur Vysya Bank",
        "karur vysya": "Karur Vysya Bank",

        "federal": "Federal Bank",

        "sbi": "State Bank of India",

        "icici": "ICICI Bank",

        "hdfc": "HDFC Bank",

        "axis": "Axis Bank",

        "indian bank": "Indian Bank"

    }


    # Check after "Debited from"

    for i, line in enumerate(ocr_result):

        if "debited from" in line.lower():

            for j in range(i+1, min(i+5, len(ocr_result))):

                text = ocr_result[j].lower()

                for key,value in bank_keywords.items():

                    if key in text:

                        return value


    # fallback

    full = " ".join(ocr_result).lower()

    for key,value in bank_keywords.items():

        if key in full:

            return value


    return bank