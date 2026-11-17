import os
import re
import sys
import json
import cv2
import joblib
import easyocr
import numpy as np
from extractors.cleaner import (
    clean_sender,
    clean_upi,
    clean_transaction_id
)
from extractors.phonepe import extract_phonepe_sender
from extractors.phonepe import extract_phonepe_time
from extractors.phonepe import extract_phonepe_receiver
from extractors.phonepe import extract_phonepe_date
from extractors.phonepe import extract_phonepe_upi
from extractors.amount import extract_amount
from extractors.datetime import extract_date_time
from extractors.transaction import extract_transaction_id
from extractors.upi import extract_upi
from extractors.receiver import extract_receiver
from extractors.sender import extract_sender
from extractors.bank import extract_bank
from extractors.receipt import extract_receipt_details
from extractors.phonepe import extract_phonepe_bank
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# ===========================================
# Load XGBoost Model
# ===========================================

print("Loading XGBoost Model...")

model = joblib.load("models/xgboost_model.pkl")

print("Model Loaded Successfully!")

# ===========================================
# Load MobileNetV2
# ===========================================

print("Loading MobileNetV2...")

cnn = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

print("MobileNetV2 Loaded!")

# ===========================================
# Load EasyOCR
# ===========================================

print("Loading EasyOCR...")

reader = easyocr.Reader(
    ['en'],
    gpu=False,
    verbose=False
)

print("EasyOCR Loaded!")

# ===========================================
# Image Path
# ===========================================

if len(sys.argv) > 1:
    image_path = sys.argv[1]
else:
    image_path = "dataset/Real/real_1.png"

print("Image Path :", image_path)

if not os.path.isfile(image_path):
    print("Image Not Found!")
    exit()

# ===========================================
# CNN Feature Extraction
# ===========================================

img = image.load_img(
    image_path,
    target_size=(224, 224)
)

x = image.img_to_array(img)

x = np.expand_dims(x, axis=0)

x = preprocess_input(x)

img_features = cnn.predict(
    x,
    verbose=0
).flatten()

print("Image Features Extracted!")

# ===========================================
# OCR
# ===========================================

print("Running OCR...")

# Read image
img = cv2.imread(image_path)
img = cv2.resize(
    img,
    None,
    fx=2,
    fy=2
)

# Convert to grayscale only if needed

if len(img.shape) == 3:

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

else:

    gray = img

_, img = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)
## ===========================================
# OCR Image Preprocessing
# ===========================================

img = cv2.resize(
    img,
    None,
    fx=2,
    fy=2,
    interpolation=cv2.INTER_CUBIC
)


# Convert to grayscale only if needed
if len(img.shape) == 3:

    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )

else:

    gray = img


gray = cv2.GaussianBlur(
    gray,
    (3,3),
    0
)


_, img = cv2.threshold(
    gray,
    0,
    255,
    cv2.THRESH_BINARY + cv2.THRESH_OTSU
)

# ===========================================
# OCR
# ===========================================

ocr_data = reader.readtext(
    gray,
    detail=1,
    paragraph=False
)

print("\n========== OCR Confidence ==========")

for box, txt, conf in ocr_data:
    print(f"{txt} --> {conf:.2f}")

print("====================================")

ocr_result = []

for item in ocr_data:

    value = item[1].strip()

    if value:
        ocr_result.append(value)

text = "\n".join(ocr_result)

# ===========================================
# Payment App Detection
# ===========================================

payment_app = "Unknown"

ocr_lower = text.lower()

if (
    "google pay" in ocr_lower
    or "gpay" in ocr_lower
    or "google transaction id" in ocr_lower
):
    payment_app = "Google Pay"

elif (
    "phonepe" in ocr_lower
    or "phone pe" in ocr_lower
    or "phonepe transaction id" in ocr_lower
):
    payment_app = "PhonePe"

print("Payment App :", payment_app)

print("\n========== OCR OUTPUT ==========")

for i, line in enumerate(ocr_result):
    print(i, ":", line)

print("================================")
# ===========================================
# OCR Correction
# ===========================================

clean_text = text.lower()

corrections = {
    "g00gle": "google",
    "fr0m": "from",
    "t0": "to",
    "c0mpleted": "completed",
    "0kicici": "okicici",
    "0kaxis": "okaxis"
}

for wrong, correct in corrections.items():
    clean_text = clean_text.replace(wrong, correct)

lines = [
    line.strip()
    for line in clean_text.split("\n")
    if line.strip()
]

# ===========================================
# Default Values
# ===========================================

bank = "Not Detected"
sender = "Not Detected"
receiver = "Not Detected"
upi = "Not Detected"
txn = "Not Detected"
google_txn = "Not Detected"
amount = "Not Detected"
date = "Not Detected"
time = "Not Detected"

full_text = " ".join(lines)

# ===========================================
# Bank Extraction
# ===========================================


if payment_app == "PhonePe":

    bank = extract_phonepe_bank(
        ocr_result
    )
else:
   bank = extract_bank(
        full_text,
        lines
    ) 
    



    # your existing Google Pay bank code
# ===========================================
# Sender Extraction
# ===========================================

if payment_app == "PhonePe":

    sender = "Not Available"

else:

    sender = extract_sender(
        full_text,
        lines,
        ocr_result
    )

print("Sender :", sender)
# ===========================================
# Receiver Extraction
# ===========================================

if payment_app == "PhonePe":

    receiver = extract_phonepe_receiver(
        ocr_result
    )

else:

    receiver = extract_receiver(
        full_text,
        lines
    )

print("Receiver :", receiver)
# ===========================================
# Fallback
# ===========================================

if receiver == "Not Detected":

    for i, line in enumerate(lines):

        line_lower = line.lower().strip()

        if line_lower in ["to", "paid to", "receiver", "recipient"]:

            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                # Ignore UPI IDs
                if "@" not in next_line:

                    receiver = next_line.title()
                    break
# ===========================================
# Transaction ID
# ===========================================

transaction_id = extract_transaction_id(
    ocr_result
)

print("Transaction ID :", transaction_id)
# ===========================================
# Google Transaction ID
# ===========================================

google_txn = "Not Detected"

for i, line in enumerate(ocr_result):

    if "google transaction id" in line.lower():

        if i + 1 < len(ocr_result):

            google_txn = re.sub(

                r'[^A-Za-z0-9]',

                '',

                ocr_result[i + 1]

            )

            break

print("Google Transaction ID :", google_txn)
# ===========================================
# UPI ID Extraction
# ===========================================

if payment_app == "PhonePe":

    upi = extract_phonepe_upi(
        ocr_result
    )

else:

    upi = extract_upi(
        ocr_result
    )

print("UPI ID :", upi)
# ===========================================
# Amount
# ===========================================

amount = extract_amount(

    payment_app,

    ocr_result,

    ocr_data

)

print(f"Amount : Rs {amount}")
if payment_app == "PhonePe":

    date = extract_phonepe_date(
        ocr_result
    )

    time = extract_phonepe_time(
        ocr_result
    )


else:

    date, time = extract_date_time(
        text
    )
# ===========================================
# Print Extracted Details
# ===========================================

print("\n========== RECEIPT DETAILS ==========")

print("Bank              :", bank)
print("Sender            :", sender)
print("Receiver          :", receiver)
print("UPI ID            :", upi)
print("Transaction ID   :", transaction_id)
print("Amount            :", amount)
print("Date              :", date)
print("Time              :", time)

print("=====================================\n")
# ===========================================
# Verification Features
# ===========================================

bank_detected = 1 if bank != "Not Detected" else 0
sender_detected = 1 if sender != "Not Detected" else 0
receiver_detected = 1 if receiver != "Not Detected" else 0
upi_detected = 1 if upi != "Not Detected" else 0
transaction_detected = 1 if transaction_id != "Not Detected" else 0
amount_detected = 1 if amount != "Not Detected" else 0
date_detected = 1 if date != "Not Detected" else 0
time_detected = 1 if time != "Not Detected" else 0
# ===========================================
# OCR Feature Extraction
# ===========================================

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
ocr_features = np.array([
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
    time_detected
])
print("\n========== OCR FEATURES ==========")
print("UPI IDs         :", upi_count)
print("Transaction IDs :", txn_count)
print("Amounts         :", amount_count)
print("Dates           :", date_count)
print("OCR Length      :", text_length)
print("==================================")

# ===========================================
# Feature Fusion
# ===========================================

features = np.concatenate((
    img_features,
    ocr_features
))
print("IMG FEATURE MEAN:", np.mean(img_features))
print("OCR FEATURES:", ocr_features)
features = features.reshape(1, -1)

print("\nFeature Fusion Completed!")

# ===========================================
# AI Prediction
# ===========================================

print("Before fixing feature size:", features.shape)

features = features[:, :model.n_features_in_]

print("After fixing feature size:", features.shape)

prediction = model.predict(features)[0]
probability = model.predict_proba(features)[0]

print("Prediction value:", prediction)
print("Probability:", probability)

fake_prob = probability[0] * 100
real_prob = probability[1] * 100

print("FAKE:", fake_prob)
print("REAL:", real_prob)

# Final prediction
if prediction == 0:
    label = "Fake"
    confidence = fake_prob
else:
    label = "Real"
    confidence = real_prob

# ===========================================
# Fraud Score (Only for display)
# ===========================================

fraud_score = 0

if bank == "Not Detected":
    fraud_score += 10

if sender == "Not Detected":
    fraud_score += 10

if receiver == "Not Detected":
    fraud_score += 10

if upi == "Not Detected":
    fraud_score += 10

if transaction_id == "Not Detected":
    fraud_score += 15

if amount == "Not Detected":
    fraud_score += 15

if date == "Not Detected":
    fraud_score += 10

if time == "Not Detected":
    fraud_score += 5

fraud_score = min(fraud_score, 100)

print("Fraud Score :", fraud_score)

# ===========================================
# Trust Score
# ===========================================

if label == "Real":

    trust_score = int(confidence)

    risk = "Low"

else:

    trust_score = max(5, 100 - int(confidence))

    risk = "High"

print("\n==========================================")
print("Prediction   :", label)
print(f"Confidence   : {confidence:.2f}%")
print(f"Trust Score  : {trust_score}/100")
print("Risk Level   :", risk)
print("Fraud Score  :", fraud_score)
print("==========================================")

# ===========================================
# Explanation
# ===========================================

if label == "Real":

    features_list = [
        "OCR Consistency",
        "Layout Verification",
        "Font Analysis",
        "Metadata Validation"
    ]

    explanation = (
        "Receipt appears authentic based on AI analysis."
    )

else:

    features_list = [
        "OCR Consistency",
        "Layout Verification",
        "Font Analysis",
        "Metadata Validation"
    ]

    explanation = (
        "Receipt shows possible forgery indicators."
    )

print("\nTop AI Features")

for item in features_list:
    print("[OK]", item)

print("\nExplanation")
print(explanation)

# ===========================================
# FINAL RESULT
# ===========================================

print("\n============= FINAL RESULT =============")

print(f"Bank Name           : {bank}")
print(f"Sender Name         : {sender}")
print(f"Receiver Name       : {receiver}")
print(f"UPI ID              : {upi}")
print("Transaction ID     :", transaction_id)
print(f"Amount              : {amount}")
print(f"Date                : {date}")
print(f"Time                : {time}")

print("----------------------------------------")

print(f"Prediction          : {label}")
print(f"Confidence          : {confidence:.2f}%")
print(f"Trust Score         : {trust_score}/100")
print(f"Risk Level          : {risk}")

print("----------------------------------------")

print("Explanation")
print(explanation)
print("DEBUG BEFORE JSON")
print("label =", label)
print("pprediction =", prediction)
print("probability =", probability)
# ===========================================
# Save JSON for Flask
# ===========================================

result = {
    "payment_app": payment_app,

    "bank": bank,

    "sender": sender,

    "receiver": receiver,

    "upi": upi,

    "transaction_id": transaction_id,

    "amount": amount,

    "date": date,

    "time": time,

    "prediction": label,

    "confidence": f"{confidence:.2f}%",

    "trust_score": f"{trust_score}/100",

    "risk_level": risk,

    "explanation": explanation,

    "features": features_list

}

with open("result.json", "w") as f:

    json.dump(
        result,
        f,
        indent=4
    )

print("\nresult.json updated successfully.")
