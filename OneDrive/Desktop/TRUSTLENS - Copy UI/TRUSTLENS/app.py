import os
import json
import sqlite3
import subprocess
import sys
import numpy as np
from flask import session
import pandas as pd
import re
from explainable_ai import generate_heatmap, generate_explanation
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image

from datetime import datetime

from flask import Flask, render_template, request, send_from_directory

from tensorflow.keras.preprocessing import image

from report_generator import create_report



app = Flask(__name__)

app = Flask(__name__)

app.secret_key = "trustlens_secret_key"



# ===============================
# LOAD AI MODEL
# ===============================
import joblib

model = joblib.load("models/xgboost_model.pkl")
print(model.classes_)
feature_model = MobileNetV2(
    weights="imagenet",
    include_top=False,
    pooling="avg"
)
print(type(model))
print(model.n_features_in_)

# ===============================
# DATABASE INITIALIZATION
# ===============================

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        image TEXT,

        prediction TEXT,

        confidence TEXT,

        trust_score TEXT,

        risk_level TEXT,

        date TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(verification_history)")
    columns = {row[1] for row in cursor.fetchall()}
    if "report_path" not in columns:
        cursor.execute(
            "ALTER TABLE verification_history ADD COLUMN report_path TEXT"
        )

    report_directory = os.path.join("static", "reports")
    if os.path.isdir(report_directory):
        reports_by_minute = {}
        report_pattern = re.compile(r"TrustLens_Report_(\d{8}_\d{6})\.pdf\Z")

        for filename in os.listdir(report_directory):
            match = report_pattern.fullmatch(filename)
            if not match:
                continue
            report_time = datetime.strptime(
                match.group(1),
                "%Y%m%d_%H%M%S"
            )
            minute = report_time.strftime("%Y%m%d_%H%M")
            reports_by_minute.setdefault(minute, []).append(
                (report_time, f"reports/{filename}")
            )

        cursor.execute(
            """
            SELECT id, date
            FROM verification_history
            WHERE report_path IS NULL AND date IS NOT NULL
            ORDER BY id
            """
        )
        records_by_minute = {}
        for record_id, record_date in cursor.fetchall():
            try:
                record_time = datetime.strptime(
                    record_date,
                    "%d-%b-%Y %I:%M %p"
                )
            except ValueError:
                continue
            minute = record_time.strftime("%Y%m%d_%H%M")
            records_by_minute.setdefault(minute, []).append(record_id)

        for minute, record_ids in records_by_minute.items():
            reports = sorted(reports_by_minute.get(minute, []))
            if len(record_ids) != len(reports):
                continue
            for record_id, (_, report_path) in zip(record_ids, reports):
                cursor.execute(
                    """
                    UPDATE verification_history
                    SET report_path = ?
                    WHERE id = ? AND report_path IS NULL
                    """,
                    (report_path, record_id)
                )

    conn.commit()

    conn.close()



init_db()





# ===============================
# UPLOAD FOLDER
# ===============================

UPLOAD_FOLDER = "static/uploads"


if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# ===============================
# FEATURE EXTRACTION FUNCTION
# ===============================

def extract_features(img_path):

    # -------- IMAGE FEATURES --------

    img = image.load_img(
        img_path,
        target_size=(224,224)
    )

    img_array = image.img_to_array(img)

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    img_array = preprocess_input(img_array)


    image_features = feature_model.predict(
        img_array,
        verbose=0
    )

    image_features = image_features.flatten()



    # -------- OCR FEATURES --------

    # read OCR text from uploaded image
    # temporary empty values
    # we will connect OCR next

    text = ""


    upi_count = len(
        re.findall(r'[\w\.-]+@[\w]+', text)
    )

    txn_count = len(
        re.findall(r'\b\d{10,18}\b', text)
    )

    amount_count = len(
        re.findall(r'\d+(?:\.\d{2})?', text)
    )

    date_count = len(
        re.findall(
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)',
            text
        )
    )

    text_length = len(text)



    ocr_features = [
        upi_count,
        txn_count,
        amount_count,
        date_count,
        text_length
    ]



    # -------- COMBINE --------

    final_features = np.concatenate(
        [
            image_features,
            ocr_features
        ]
    )


    print("FINAL FEATURES:", final_features.shape)


    return final_features
# ===============================
# AI PREDICTION FUNCTION (XGBoost)
# ===============================

def predict_receipt(img_path):

    # Extract 1285 features from uploaded image
    features = extract_features(img_path)


    # Convert to DataFrame
    features = pd.DataFrame([features])


    print("FEATURE SHAPE BEFORE MODEL:", features.shape)


    # Load training feature names
    training_df = pd.read_csv(
        "results/fusion_features.csv"
    )
    

    # Remove non-feature columns
    feature_columns = training_df.drop(
        columns=["label", "filename"]
    ).columns


    # Apply exact training column names
    features.columns = feature_columns


    print("FEATURE SHAPE AFTER COLUMN MATCH:", features.shape)
    print("LAST FEATURES:")
    print(features.columns[-10:])


    # XGBoost prediction
    prediction = model.predict(features)

    probability = model.predict_proba(features)


    print("XGBOOST OUTPUT:", prediction)
    print("PROBABILITY:", probability)


    # Label mapping
    # 0 = Fake
    # 1 = Real

    fake_prob = probability[0][0] * 100
    real_prob = probability[0][1] * 100

    print("FAKE PROBABILITY:", fake_prob)
    print("REAL PROBABILITY:", real_prob)

    difference = abs(real_prob - fake_prob)

    print("PROBABILITY DIFFERENCE:", difference)


# Handle uncertain predictions
    if difference < 10:

      label = "Fake"
      score = fake_prob

    else:

        if real_prob > fake_prob:

           label = "Real"
           score = real_prob

        else:

           label = "Fake"
           score = fake_prob
    explanation = generate_detailed_reason(
    img_path,
    label,
    score
)


    return label, round(score,2), explanation

# ==========================================
# ADVANCED EXPLAINABLE AI MODULE
# ==========================================

def generate_detailed_reason(img_path, prediction, confidence):

    reasons = []

    # Extract features
    features = extract_features(img_path)


    # OCR based features
    upi_count = features[-5]
    txn_count = features[-4]
    amount_count = features[-3]
    date_count = features[-2]
    text_length = features[-1]


    # -------------------------------
    # 1. Text Density Analysis
    # -------------------------------

    if text_length < 150:

        reasons.append(
            "Low text density detected. "
            "The receipt contains limited textual information "
            "compared with genuine transaction receipts."
        )

    else:

        reasons.append(
            "Text density is consistent with normal digital payment receipts."
        )



    # -------------------------------
    # 2. Transaction Pattern Analysis
    # -------------------------------

    if txn_count < 1:

        reasons.append(
            "Transaction reference pattern is not detected. "
            "Genuine payment receipts usually contain unique transaction identifiers."
        )

    else:

        reasons.append(
            "Transaction reference pattern detected successfully."
        )



    # -------------------------------
    # 3. UPI Structure Analysis
    # -------------------------------

    if upi_count < 1:

        reasons.append(
            "UPI identifier structure could not be verified. "
            "The payment identity information appears inconsistent."
        )

    else:

        reasons.append(
            "UPI identifier format matches expected payment patterns."
        )



    # -------------------------------
    # 4. Amount and Date Relationship
    # -------------------------------

    if amount_count > 0 and date_count > 0:

        reasons.append(
            "Amount and date information were detected "
            "and compared with learned receipt patterns."
        )

    else:

        reasons.append(
            "Important transaction attributes show abnormal patterns."
        )



    # -------------------------------
    # 5. Image AI Analysis
    # -------------------------------

    if confidence >= 90:

        reasons.append(
            "Deep learning feature analysis shows a strong similarity "
            "with previously learned receipt patterns."
        )


    elif confidence >= 70:

        reasons.append(
            "Moderate similarity detected. "
            "Some visual characteristics differ from training examples."
        )


    else:

        reasons.append(
            "Significant visual deviation detected from genuine receipt samples."
        )



    # -------------------------------
    # Final Decision Explanation
    # -------------------------------

    if prediction == "Fake" or confidence < 70:

        reasons.append(
            "Final decision: The receipt contains multiple patterns "
            "associated with manipulated or synthetic receipts."
        )

    else:

        reasons.append(
            "Final decision: The receipt follows the learned structure "
            "and appearance of authentic transaction receipts."
        )


    return reasons
# ===============================
# HOME PAGE
# ===============================

@app.route("/")
def home():

    return render_template("index.html")


@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "GET":
        return render_template("upload.html")

    if "receipt" not in request.files:
        return render_template(
            "upload.html",
            error_message="Choose a receipt image before starting the analysis."
        ), 400

    file = request.files["receipt"]

    if file.filename == "":
        return render_template(
            "upload.html",
            error_message="Choose a receipt image before starting the analysis."
        ), 400

    image_name = secure_filename(file.filename)
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    extension = os.path.splitext(image_name)[1].lower()

    if not image_name or extension not in allowed_extensions:
        return render_template(
            "upload.html",
            error_message="Use a PNG, JPG, JPEG, or WEBP receipt image."
        ), 400

    try:
        with Image.open(file.stream) as receipt_image:
            if receipt_image.format not in {"PNG", "JPEG", "WEBP"}:
                return render_template(
                    "upload.html",
                    error_message="The selected file is not a supported receipt image."
                ), 400
            receipt_image.verify()
    except (UnidentifiedImageError, OSError):
        return render_template(
            "upload.html",
            error_message="The selected file could not be read as an image. Choose a valid receipt image."
        ), 400

    file.stream.seek(0)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)

    file.save(save_path)

    
    # -----------------------------
    # Run OCR Parser
    # -----------------------------

    result = subprocess.run(
        [sys.executable, "test_image.py", save_path],
        capture_output=True,
        text=True
    )

    print("TEST IMAGE OUTPUT:")
    print(result.stdout)

    print("TEST IMAGE ERROR:")
    print(result.stderr)

    if result.returncode != 0:
        return render_template(
            "upload.html",
            error_message="Receipt analysis could not be completed. Please try again with a clear receipt image."
        ), 500
    # -----------------------------
    # Read Latest result.json
    # -----------------------------

    with open("result.json", "r", encoding="utf-8") as f:
        result = json.load(f)

    print("\nLATEST JSON")
    print(result)

    # -----------------------------
    # Update AI values only
    # -----------------------------
    ai_prediction = result["prediction"]
    ai_confidence = float(result["confidence"].replace("%",""))
    ai_explanation = result["explanation"]
    heatmap_path = generate_heatmap(
    save_path
)
    heatmap_path = heatmap_path.replace("\\","/")
    print("HEATMAP CREATED:", heatmap_path)
    session["heatmap_path"] = heatmap_path

    xai_scores, reasons = generate_explanation()
    result["prediction"] = ai_prediction
    
    result["confidence"] = f"{ai_confidence:.2f}%"
    result["trust_score"] = f"{int(ai_confidence)}/100"
    result["explanation"] = ai_explanation
    if ai_prediction == "Real":

        result["risk_level"] = "Low"

        result["explanation"] = ai_explanation
    else:

        result["risk_level"] = "High"
        result["explanation"] = ai_explanation

    if "features" not in result:

        result["features"] = [

            "OCR Consistency",

            "Layout Verification",

            "Font Analysis",

            "Metadata Validation"

        ]

    # -----------------------------
    # Generate PDF
    # -----------------------------

    report_path = create_report(

        save_path,

        result["bank"],

        result["sender"],

        result["receiver"],

        result["upi"],

        result["transaction_id"],

        result["transaction_id"],

        result["amount"],

        result["date"],

        result["time"],

        result["prediction"],

        result["confidence"],

        result["trust_score"],

        result["risk_level"],

        result["explanation"],

        result["features"],
        heatmap_path,

        xai_scores,

        reasons,
        payment_app=result.get("payment_app")

    )
    print("Returned report path:", report_path)
    report_path = os.path.relpath(report_path, "static")
    report_path = report_path.replace("\\", "/")

    print(report_path)
    # -----------------------------
    # Save History
    # -----------------------------

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO verification_history
        (image,prediction,confidence,trust_score,risk_level,date,report_path)
        VALUES(?,?,?,?,?,?,?)
        """,
        (
            image_name,
            result["prediction"],
            result["confidence"],
            result["trust_score"],
            result["risk_level"],
            datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            report_path
        )
    )

    conn.commit()

    conn.close()

    # -----------------------------
    # IMPORTANT
    # -----------------------------

    print("\nFINAL RESULT SENT TO WEBSITE")
    print(result)

    return render_template(
        "result.html",
        result=result,
        image=image_name,
        report=report_path,
        heatmap=heatmap_path,
        xai_scores=xai_scores,
        reasons=reasons
    )



# ===============================
# HISTORY PAGE
# ===============================

@app.route("/history")

def history():


    conn = sqlite3.connect("database.db")


    cursor = conn.cursor()



    cursor.execute(

        "SELECT * FROM verification_history ORDER BY id DESC"

    )



    records = cursor.fetchall()



    conn.close()



    return render_template(

        "history.html",

        records=records

    )


@app.route("/history/<int:record_id>/report")
def download_report(record_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT report_path FROM verification_history WHERE id = ?",
        (record_id,)
    )
    record = cursor.fetchone()
    conn.close()

    if record is None or not record[0]:
        return "Report is not available for this verification.", 404

    report_path = record[0].replace("\\", "/")
    report_directory, _, filename = report_path.partition("/")
    if (
        report_directory != "reports"
        or not filename
        or filename != os.path.basename(filename)
        or not filename.lower().endswith(".pdf")
    ):
        return "Report is not available for this verification.", 404

    return send_from_directory(
        os.path.join(app.root_path, "static", "reports"),
        filename,
        as_attachment=True,
        download_name=f"TrustLens_Report_{record_id}.pdf"
    )



@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM verification_history"
    )

    total = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM verification_history WHERE prediction='Real'"
    )

    real = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM verification_history WHERE prediction='Fake'"
    )

    fake = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT *
        FROM verification_history
        ORDER BY id DESC
        LIMIT 5
        """
    )

    recent = cursor.fetchall()


    trust_scores = []


    for row in recent:

        try:

            score = row[4].split("/")[0]

            trust_scores.append(
                int(score)
            )

        except:

            trust_scores.append(0)



    conn.close()



    xai_scores = {

        "Image Analysis":85,

        "OCR Analysis":75,

        "Transaction Pattern":90,

        "Visual Similarity":80

    }

    reasons = [

    "Low text density detected",

    "Transaction reference pattern is abnormal",

    "UPI identifier structure mismatch",

    "Visual deviation detected from genuine receipts"

]
    explanation = [

    "Low text density detected in receipt",

    "Transaction reference pattern is abnormal",

    "UPI identifier structure could not be verified",

    "Visual deviation detected from genuine receipt samples",

    "Multiple synthetic receipt indicators found"

]

    heatmap_path = session.get(
        "heatmap_path",
        None
    )



    return render_template(

        "dashboard.html",

        total=total,

        real=real,

        fake=fake,

        recent=recent,

        trust_scores=trust_scores,

        xai_scores=xai_scores,

        heatmap_path=heatmap_path,
        reasons=reasons,

        explanation= explanation
    )

# ===============================
# RUN APPLICATION
# ===============================


if __name__ == "__main__":

    app.run(debug=True)
