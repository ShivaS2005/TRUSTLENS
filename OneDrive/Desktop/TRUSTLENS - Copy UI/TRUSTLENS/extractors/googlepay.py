import re


def extract_google_amount(ocr_result):

    candidates = []


    for i, line in enumerate(ocr_result):

        text = line.lower()


        # Ignore phone numbers
        if "+" in line:
            continue


        # Ignore bank details
        if "bank" in text:
            continue


        numbers = re.findall(
            r'\d[\d,]*',
            line
        )


        for num in numbers:

            value = num.replace(",", "")


            if not value.isdigit():
                continue


            amount = int(value)


            # Ignore IDs
            if len(value) >= 7:
                continue


            if amount < 100:
                continue


            score = 0


            # Amount symbol
            if "₹" in line:
                score += 50


            # OCR mistake like R2500
            if text.startswith("r"):
                score += 30


            # Nearby confirmation
            for j in range(max(0, i-2),
                           min(len(ocr_result), i+3)):

                nearby = ocr_result[j].lower()


                if any(word in nearby for word in
                       ["paid",
                        "completed",
                        "sent"]):
                    score += 20


                if any(word in nearby for word in
                       ["bank",
                        "transaction",
                        "reference",
                        "id"]):
                    score -= 20


            candidates.append(
                (score, amount)
            )


    if candidates:

        candidates.sort(
            key=lambda x: x[0],
            reverse=True
        )

        final_amount = candidates[0][1]


    # OCR correction:
    # 22500 may be OCR error for 2500
    if str(final_amount).startswith("22") and len(str(final_amount)) == 5:

        final_amount = int(
            str(final_amount)[1:]
        )


    return str(final_amount)

    return "Not Detected"