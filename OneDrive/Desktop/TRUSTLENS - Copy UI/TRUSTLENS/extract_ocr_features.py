import os
import re
import pandas as pd

OCR_FOLDER = "results/ocr"

rows = []

for file in os.listdir(OCR_FOLDER):

    if not file.endswith(".txt"):
        continue

    filepath = os.path.join(OCR_FOLDER, file)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    # =====================================
    # Original OCR Features
    # =====================================

    upi_count = len(re.findall(
        r'[A-Za-z0-9._%-]+@[A-Za-z0-9._-]+',
        text,
        re.IGNORECASE
    ))

    txn_count = len(re.findall(
        r'\b[A-Za-z0-9]{10,25}\b',
        text
    ))

    amount_count = len(re.findall(
        r'(?:Rs\.?|INR)?\s?\d[\d,]*(?:\.\d{2})?',
        text,
        re.IGNORECASE
    ))

    date_count = len(re.findall(
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
        text,
        re.IGNORECASE
    ))

    text_length = len(text)

    # =====================================
    # Extra Detection Features
    # =====================================

    lower = text.lower()

    bank_detected = int(any(bank in lower for bank in [
        "hdfc",
        "icici",
        "axis",
        "sbi",
        "indian bank",
        "federal",
        "karur vysya",
        "kvb"
    ]))

    sender_detected = int("from" in lower)

    receiver_detected = int(
        "paid to" in lower or
        "to" in lower or
        "sent to" in lower
    )

    upi_detected = int("@" in text)

    transaction_detected = int(
        "transaction id" in lower or
        "utr" in lower or
        "google transaction id" in lower or
        "phonepe transaction id" in lower
    )

    amount_detected = int(amount_count > 0)

    date_detected = int(date_count > 0)

    time_detected = int(bool(
        re.search(
            r'\d{1,2}:\d{2}\s?(am|pm)',
            lower
        )
    ))

    label = "Real" if file.lower().startswith("real") else "Fake"

    rows.append([
        file.replace(".txt", ".png"),

        upi_count,
        txn_count,
        amount_count,
        date_count,
        text_length,

        bank_detected,
        sender_detected,
        receiver_detected,
        upi_detected,
        transaction_detected,
        amount_detected,
        date_detected,
        time_detected,

        label
    ])

df = pd.DataFrame(rows, columns=[
    "filename",

    "upi_count",
    "txn_count",
    "amount_count",
    "date_count",
    "text_length",

    "bank_detected",
    "sender_detected",
    "receiver_detected",
    "upi_detected",
    "transaction_detected",
    "amount_detected",
    "date_detected",
    "time_detected",

    "label"
])

os.makedirs("results", exist_ok=True)

df.to_csv(
    "results/ocr_features.csv",
    index=False
)

print(df.head())
print("\nOCR Features Saved Successfully!")
print("Shape:", df.shape)