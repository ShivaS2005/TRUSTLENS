import re


def extract_generic_amount(ocr_data):

    candidates = []

    for i, item in enumerate(ocr_data):

        text = item[1].strip()

        nums = re.findall(r'[\d,]+', text)

        for num in nums:

            digits = num.replace(",", "")

            if not digits.isdigit():
                continue

            value = int(digits)

            # Ignore small numbers
            if value < 100:
                continue

            # Ignore phone numbers / transaction IDs
            if len(digits) >= 10:
                continue


            score = 0

            context = text.lower()


            # Currency symbol
            if "₹" in text or "rs" in context:
                score += 15


            # Comma formatted amount
            if "," in num:
                score += 5


            # OCR confidence
            confidence = item[2]

            score += confidence * 5


            # Check nearby OCR text
            for j in range(max(0, i-2), min(len(ocr_data), i+3)):

                nearby = ocr_data[j][1].lower()


                if any(k in nearby for k in
                       ["paid", "amount", "completed",
                        "debited", "credited"]):

                    score += 8


                if any(k in nearby for k in
                       ["transaction", "utr",
                        "upi id", "reference"]):

                    score -= 8


            candidates.append(
                (score, value)
            )


    if candidates:

        candidates.sort(
            reverse=True
        )

        return str(
            candidates[0][1]
        )


    return "Not Detected"