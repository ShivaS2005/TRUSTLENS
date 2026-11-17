import re
from extractors.cleaner import clean_upi


def extract_upi(ocr_result):

    upi = "Not Detected"

    domains = [

    "hdfcbank",
    "okhdfcbank",
    "paytm",
    "okicici",
    "okaxis",
    "oksbi",
    "ybl",
    "ibl",
    "axl",
    "ptyes",
    "airtel"

]

    # -----------------------------
    # First search inside "To" block
    # -----------------------------

    for i, line in enumerate(ocr_result):

        if line.lower().strip() == "to":

            for j in range(i + 1, min(i + 5, len(ocr_result))):

                temp = ocr_result[j].lower().replace(" ", "")

                if "bank" in temp:
                    continue

                for domain in domains:

                    if domain in temp:

                        pos = temp.find(domain)

                        user = temp[:pos]

                        user = re.sub(
                            r'[^a-z0-9._-]',
                            '',
                            user
                        )

                        if len(user) >= 3:

                            upi = user + "@" + domain

                            break

                if upi != "Not Detected":
                    break

            break

    # -----------------------------
    # Fallback
    # -----------------------------

    if upi == "Not Detected":

        for line in ocr_result:

            temp = line.lower().replace(" ", "")

            for domain in domains:

                if domain in temp:

                    pos = temp.find(domain)

                    user = temp[:pos]

                    user = re.sub(
                        r'[^a-z0-9._-]',
                        '',
                        user
                    )

                    if len(user) >= 3:

                        upi = user + "@" + domain

                        break

            if upi != "Not Detected":
                break

    upi = clean_upi(upi)

    return upi