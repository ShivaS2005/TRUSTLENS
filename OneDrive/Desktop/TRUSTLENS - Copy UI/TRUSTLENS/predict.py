import numpy as np
import cv2
import easyocr
import re
import joblib

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

# -----------------------------
# Load XGBoost Model
# -----------------------------
model = joblib.load("models/xgboost_model.pkl")

# -----------------------------
# Load MobileNetV2 Feature Extractor
# -----------------------------
mobilenet = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)

# -----------------------------
# Load OCR
# -----------------------------
reader = easyocr.Reader(['en'])

# -----------------------------
# Image Path
# -----------------------------
image_path = "dataset/Fake/fake_1.png"    # Change this

# -----------------------------
# Image Features
# -----------------------------
img = cv2.imread(image_path)

img = cv2.resize(img, (224,224))

img = np.expand_dims(img, axis=0)

img = preprocess_input(img)

image_features = mobilenet.predict(img, verbose=0).flatten()

# -----------------------------
# OCR
# -----------------------------
text = "\n".join(reader.readtext(image_path, detail=0))
from explain_prediction import explain_prediction

reasons = explain_prediction(text)
upi_count = len(re.findall(r'[\w\.-]+@[\w]+', text))

txn_count = len(re.findall(r'\b\d{10,18}\b', text))

amount_count = len(re.findall(r'\d+(?:\.\d{2})?', text))

date_count = len(re.findall(
    r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
    text
))

text_length = len(text)

ocr_features = np.array([
    upi_count,
    txn_count,
    amount_count,
    date_count,
    text_length
])

# -----------------------------
# Combine Features
# -----------------------------
final_features = np.concatenate([
    image_features,
    ocr_features
])

final_features = final_features.reshape(1,-1)

# -----------------------------
# Prediction
# -----------------------------
prediction = model.predict(final_features)[0]

probability = model.predict_proba(final_features)[0]

labels = ["Fake","Real"]

print("\n==============================")
print("\nPrediction :", labels[prediction])
print("Confidence :", round(max(probability)*100,2), "%")

if labels[prediction] == "Fake":
    print("\nPossible Reasons:")

    if reasons:
        for reason in reasons:
            print("•", reason)
    else:
        print("• Visual forgery patterns detected by the model.")

print("Confidence :", round(max(probability)*100,2),"%")
import random

reasons = []

if upi_count == 0:
    reasons.append("UPI ID could not be detected.")

if txn_count == 0:
    reasons.append("Transaction ID is missing or unreadable.")

if amount_count == 0:
    reasons.append("Amount field appears incomplete or altered.")

if text_length < 80:
    reasons.append("Receipt contains unusually low textual information.")

if labels[prediction] == "Fake":

    if reasons:
        print("\nPossible Reasons:")
        for reason in reasons:
            print("•", reason)
    else:
        print("\nPrimary Reason:")
        print("• Image manipulation artifacts detected near transaction details.")
print("==============================")