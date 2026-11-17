import re
from extractors.cleaner import clean_sender


def extract_sender(full_text, lines, ocr_result):

    sender = "Not Detected"

    patterns = [
        r'from[: ]+([A-Za-z ]+)',
        r'paid by[: ]+([A-Za-z ]+)',
        r'sender[: ]+([A-Za-z ]+)'
    ]

    sender_matches = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            full_text,
            re.IGNORECASE
        )

        if matches:
            sender_matches.extend(matches)

    if sender_matches:

        sender = max(
            sender_matches,
            key=len
        ).strip()

        sender = re.split(
            r'google|pay|upi|transaction|bank|@|\(',
            sender,
            flags=re.IGNORECASE
        )[0].strip()

        sender = clean_sender(sender)

        return sender

    # Fallback using OCR lines
    for i, line in enumerate(ocr_result):

        if line.lower().strip() == "from":

            sender_parts = []

            for j in range(i + 1, min(i + 6, len(ocr_result))):

                value = ocr_result[j].strip()

                lower = value.lower()

                if (
                    "bank" in lower or
                    "transaction" in lower or
                    "google" in lower or
                    "phonepe" in lower or
                    "upi" in lower or
                    "@" in value or
                    "okicici" in lower or
                    "okaxis" in lower or
                    value.isdigit()
                ):
                    break

                if len(value) >= 2:
                    sender_parts.append(value)

            if sender_parts:

                sender = " ".join(sender_parts)

                break

    return clean_sender(sender)