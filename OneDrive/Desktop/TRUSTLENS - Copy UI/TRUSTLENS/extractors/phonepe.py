import re
print("LOADED PHONEPE.PY")
print("PHONEPE MODULE LOADED")
print("PHONEPE MODULE LOADED - NEW VERSION")
import re


import re


import re


def extract_phonepe_amount(ocr_result):

    # Find Paid to section
    for i, line in enumerate(ocr_result):

        if "paid to" in line.lower():

            # Receiver comes next
            for j in range(i + 1, min(i + 6, len(ocr_result))):

                text = ocr_result[j]

                # Ignore UPI ID
                if "@" in text:
                    continue

                # Remove symbols
                cleaned = re.sub(
                    r'[^0-9]',
                    '',
                    text
                )

                if cleaned:

                    value = int(cleaned)

                    # OCR correction:
                    # If OCR adds extra 8 before amount
                    # Example: 8130 -> 130
                    if (
                        value > 1000
                        and str(value).startswith("8")
                        and len(str(value)) == 4
                    ):
                        value = int(str(value)[1:])

                    # Ignore year
                    if value != 2026:

                        return str(value)

    return "Not Detected"
def extract_phonepe_bank(ocr_result):

    for i, line in enumerate(ocr_result):

        if "debited from" in line.lower():

            if i + 1 < len(ocr_result):

                bank = ocr_result[i + 1].strip()

                if "X" not in bank.upper():

                    if bank.lower() in ["k", "k'", "ktk"]:
                        return "Karur Vysya Bank"

                    return bank

    return "Not Detected"
def extract_phonepe_receiver(ocr_result):

    receiver = "Not Detected"


    for i, line in enumerate(ocr_result):

        if "paid to" in line.lower():

            # Next line is receiver name

            if i + 1 < len(ocr_result):

                candidate = ocr_result[i + 1].strip()


                # Ignore numbers

                if not candidate.isdigit():

                    # Ignore UPI IDs

                    if "@" not in candidate:

                        receiver = candidate


            break


    return receiver
import re


def extract_phonepe_date(ocr_result):

    import re


    months = {
        "january": "January",
        "february": "February",
        "march": "March",
        "april": "April",
        "may": "May",
        "june": "June",
        "july": "July",
        "august": "August",
        "september": "September",
        "october": "October",
        "november": "November",
        "december": "December"
    }


    # First priority:
    # Complete date in one OCR line

    for line in ocr_result:

        match = re.search(
            r'(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(20\d{2})',
            line,
            re.IGNORECASE
        )

        if match:

            day = match.group(1)
            month = match.group(2)
            year = match.group(3)

            return f"{day} {month} {year}"


    # Second priority:
    # Old split format

    day = None
    month = None
    year = None


    for i, line in enumerate(ocr_result):

        year_match = re.search(
            r'20\d{2}',
            line
        )

        if year_match:

            year = year_match.group()


            if i > 0:

                previous = ocr_result[i-1].strip()

                if previous.isdigit():

                    if 1 <= int(previous) <= 31:

                        day = previous



    for line in ocr_result:

        for key, value in months.items():

            if key in line.lower():

                month = value


    if day and month and year:

        return f"{day} {month} {year}"


    return "Not Detected"
def extract_phonepe_upi(ocr_result):

    import re


    full_text = " ".join(ocr_result)


    match = re.search(
        r'[\w.\-]+@[\w.\-]+',
        full_text
    )


    if match:

        return match.group()


    return "Not Detected"
def extract_phonepe_time(ocr_result):

    import re


    for line in ocr_result:

        match = re.search(
            r'(\d{1,2}:\d{2}\s?(AM|PM))',
            line,
            re.IGNORECASE
        )


        if match:

            return match.group(1)


    return "Not Detected"
def extract_phonepe_sender(ocr_result):

    for i, line in enumerate(ocr_result):

        if "debited from" in line.lower():

            if i + 1 < len(ocr_result):

                sender = ocr_result[i + 1].strip()

                # ignore account number
                if "X" not in sender.upper():

                    return sender

    return "Not Available"