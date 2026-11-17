import re

def explain_prediction(ocr_text):
    reasons = []

    # UPI ID
    upi = re.findall(r'[\w\.-]+@[\w]+', ocr_text)
    if len(upi) == 0:
        reasons.append("No UPI ID detected")

    # Transaction ID
    txn = re.findall(r'\b\d{10,18}\b', ocr_text)
    if len(txn) == 0:
        reasons.append("Transaction ID missing")

    # Amount
    amount = re.findall(r'\d+(?:\.\d{2})?', ocr_text)
    if len(amount) == 0:
        reasons.append("Amount not detected")

    # Bank Name
    banks = [
        "SBI",
        "HDFC",
        "ICICI",
        "Axis",
        "Federal",
        "Canara",
        "Indian Bank",
        "Kotak"
    ]

    found_bank = any(bank.lower() in ocr_text.lower() for bank in banks)

    if not found_bank:
        reasons.append("Bank name missing")

    return reasons