import re


def extract_date_time(text):

    date = "Not Detected"
    time = "Not Detected"

    # -------------------------
    # Date
    # -------------------------

    date_patterns = [

        r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',

        r'\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}',

        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}'

    ]

    for pattern in date_patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            date = match.group()
            break

    # -------------------------
    # Time
    # -------------------------

    match = re.search(

        r'\d{1,2}[:.]\d{2}\s?(?:AM|PM|am|pm)',

        text

    )

    if match:

        time = (
            match.group()
            .replace(".", ":")
            .upper()
        )

    return date, time