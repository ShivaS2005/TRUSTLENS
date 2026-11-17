import re


def extract_receiver(full_text, lines):

    receiver = "Not Detected"

    patterns = [
        r'paid to[: ]+([A-Za-z ]+)',
        r'to[: ]+([A-Za-z ]+)',
        r'receiver[: ]+([A-Za-z ]+)',
        r'recipient[: ]+([A-Za-z ]+)',
        r'sent to[: ]+([A-Za-z ]+)'
    ]

    receiver_matches = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            full_text,
            re.IGNORECASE
        )

        if matches:
            receiver_matches.extend(matches)

    if receiver_matches:

        cleaned = []

        for name in receiver_matches:

            name = re.split(
                r'google|pay|upi|transaction|@|\(',
                name,
                flags=re.IGNORECASE
            )[0].strip()

            if len(name) > 2:

                cleaned.append(name)

        if cleaned:

            receiver = max(
                cleaned,
                key=len
            ).title()

            return receiver

    # ----------------------------
    # Fallback
    # ----------------------------

    for i, line in enumerate(lines):

        value = line.lower().strip()

        if value in [

            "to",

            "paid to",

            "receiver",

            "recipient"

        ]:

            if i + 1 < len(lines):

                next_line = lines[i + 1].strip()

                if "@" not in next_line:

                    receiver = next_line.title()

                    break

    return receiver