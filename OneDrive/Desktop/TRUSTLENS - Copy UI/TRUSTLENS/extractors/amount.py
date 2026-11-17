from extractors.googlepay import extract_google_amount
from extractors.phonepe import extract_phonepe_amount
from extractors.generic import extract_generic_amount


def extract_amount(payment_app, ocr_result, ocr_data):

    if payment_app == "Google Pay":

        return extract_google_amount(
            ocr_result
        )

    elif payment_app == "PhonePe":

        return extract_phonepe_amount(
            ocr_result
        )

    else:

        return extract_generic_amount(
            ocr_data
        )