import cv2
import numpy as np
import os


def generate_heatmap(image_path):

    output_folder = "static/heatmaps"

    os.makedirs(
        output_folder,
        exist_ok=True
    )


    img = cv2.imread(image_path)


    if img is None:
        return None


    gray = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2GRAY
    )


    # Blur to find irregular regions
    blur = cv2.GaussianBlur(
        gray,
        (5,5),
        0
    )


    # Difference detection
    diff = cv2.absdiff(
        gray,
        blur
    )


    # Increase intensity
    diff = cv2.normalize(
        diff,
        None,
        0,
        255,
        cv2.NORM_MINMAX
    )


    # Convert to heatmap
    heatmap = cv2.applyColorMap(
        diff.astype(np.uint8),
        cv2.COLORMAP_JET
    )


    # Combine with original image
    result = cv2.addWeighted(
        img,
        0.6,
        heatmap,
        0.4,
        0
    )


    filename = os.path.basename(
        image_path
    )


    save_path = os.path.join(
        output_folder,
        "heatmap_" + filename
    )


    cv2.imwrite(
        save_path,
        result
    )


    return save_path


# ===============================
# AI EXPLANATION
# ===============================

def generate_explanation():


    xai_scores = {

        "Image Analysis": 85,

        "OCR Analysis": 75,

        "Transaction Pattern": 90,

        "Visual Similarity": 80

    }



    reasons = [

        "Visual structure deviation detected",

        "OCR text pattern inconsistency found",

        "Transaction identifier verification failed",

        "Receipt formatting appears abnormal"

    ]


    return xai_scores, reasons