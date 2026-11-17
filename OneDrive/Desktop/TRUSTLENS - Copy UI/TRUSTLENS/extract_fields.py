import easyocr
import re
import os

reader = easyocr.Reader(['en'])

image_path = "dataset_split/test/Real/real_10.png"

text = "\n".join(reader.readtext(image_path, detail=0))

print("========== OCR TEXT ==========")
print(text)

# --------------------------
# Extract UPI ID
# --------------------------
upi = re.findall(r'[\w\.-]+@[\w]+', text)

# --------------------------
# Extract UPI Transaction ID
# --------------------------
upi_txn = re.findall(r'\b\d{10,18}\b', text)

# --------------------------
# Extract Google Transaction ID
# --------------------------
google_txn = re.findall(r'C[A-Za-z0-9]{8,}', text)

# --------------------------
# Extract Amount
# --------------------------
amount = re.findall(r'\b\d{1,6}(?:\.\d{2})?\b', text)

# --------------------------
# Extract Date
# --------------------------
date = re.findall(
    r'\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b',
    text
)

print("\n========== EXTRACTED FIELDS ==========")

print("UPI IDs:", upi)
print("UPI Transaction IDs:", upi_txn)
print("Google Transaction IDs:", google_txn)
print("Amount:", amount)
print("Date:", date)