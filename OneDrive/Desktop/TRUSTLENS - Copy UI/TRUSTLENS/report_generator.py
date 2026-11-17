import os
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


INK = colors.HexColor("#1c2924")
MUTED = colors.HexColor("#737d75")
GREEN = colors.HexColor("#337c60")
GREEN_DARK = colors.HexColor("#253c31")
GREEN_PALE = colors.HexColor("#eaf3ed")
PAPER = colors.HexColor("#f5f6f1")
LINE = colors.HexColor("#e6e9e1")
AMBER = colors.HexColor("#a66c20")
WHITE = colors.white


def _text(value):
    if value is None or value == "":
        return "Not available"
    return escape(str(value))


def _section_heading(title, subtitle=None, styles=None):
    content = [Paragraph(escape(title), styles["SectionHeading"])]
    if subtitle:
        content.append(Paragraph(escape(subtitle), styles["SectionSubtitle"]))
    content.append(Spacer(1, 9))
    return content


def _page_chrome(canvas, document):
    canvas.saveState()
    page_width, page_height = A4

    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, page_height - 8, page_width, 8, fill=1, stroke=0)

    canvas.setFillColor(GREEN)
    canvas.roundRect(document.leftMargin, page_height - 39, 19, 19, 5, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawCentredString(document.leftMargin + 9.5, page_height - 32, "T")
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawString(document.leftMargin + 27, page_height - 31, "TRUSTLENS")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(page_width - document.rightMargin, page_height - 31, "PAYMENT RECEIPT REVIEW")

    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    canvas.line(document.leftMargin, 38, page_width - document.rightMargin, 38)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(document.leftMargin, 25, "AI-assisted assessment · Confirm payment independently with your payment provider.")
    canvas.drawRightString(page_width - document.rightMargin, 25, f"{document.page}")
    canvas.restoreState()


def create_report(
        image_path,
        bank,
        sender,
        receiver,
        upi,
        txn,
        google_txn,
        amount,
        date,
        time,
        prediction,
        confidence,
        trust,
        risk,
        explanation,
        features,
        heatmap_path,
        xai_scores,
        reasons,
        payment_app=None):
    report_directory = os.path.join("static", "reports")
    os.makedirs(report_directory, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    pdf_path = os.path.join(
        report_directory,
        f"TrustLens_Report_{timestamp}.pdf"
    )
    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=57,
        bottomMargin=53,
        title="TrustLens Receipt Review",
        author="TrustLens",
        subject="AI-assisted digital payment receipt review",
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportEyebrow",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=GREEN,
        spaceAfter=6,
        tracking=1.1,
    ))
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=25,
        leading=30,
        alignment=TA_LEFT,
        textColor=INK,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=9,
        leading=14,
        textColor=MUTED,
        spaceAfter=15,
    ))
    styles.add(ParagraphStyle(
        name="VerdictLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=10,
        textColor=colors.HexColor("#c5d8ca"),
        tracking=1,
    ))
    styles.add(ParagraphStyle(
        name="VerdictValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=23,
        textColor=WHITE,
    ))
    styles.add(ParagraphStyle(
        name="VerdictCopy",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#dce8df"),
    ))
    styles.add(ParagraphStyle(
        name="MetricLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=6.5,
        leading=9,
        textColor=MUTED,
        tracking=.5,
    ))
    styles.add(ParagraphStyle(
        name="MetricValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=INK,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=INK,
        spaceBefore=5,
        spaceAfter=0,
    ))
    styles.add(ParagraphStyle(
        name="SectionSubtitle",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=MUTED,
    ))
    styles.add(ParagraphStyle(
        name="TableLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=MUTED,
    ))
    styles.add(ParagraphStyle(
        name="TableValue",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=INK,
        wordWrap="CJK",
    ))
    styles.add(ParagraphStyle(
        name="BodyCopy",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=13,
        textColor=colors.HexColor("#526057"),
    ))
    styles.add(ParagraphStyle(
        name="SmallCopy",
        parent=styles["Normal"],
        fontSize=7.5,
        leading=11,
        textColor=MUTED,
    ))
    is_positive = str(prediction).strip().lower() == "real"
    verdict_color = GREEN_DARK if is_positive else colors.HexColor("#684725")
    verdict_summary = (
        "The model found receipt signals that appear consistent. "
        "This image alone does not confirm that a payment was made."
        if is_positive else
        "The model found signals that may need closer inspection. "
        "Confirm the transaction through your payment provider."
    )
    safe_features = features or []
    safe_scores = xai_scores or {}
    safe_reasons = reasons or []
    story = [
        Paragraph("RECEIPT REVIEW / GENERATED " + datetime.now().strftime("%d %b %Y · %I:%M %p"), styles["ReportEyebrow"]),
        Paragraph("Verification report", styles["ReportTitle"]),
        Paragraph("A readable summary of the receipt details and AI-assisted signals reviewed.", styles["ReportSubtitle"]),
    ]

    verdict = Table(
        [[
            [
                Paragraph("MODEL ASSESSMENT", styles["VerdictLabel"]),
                Spacer(1, 5),
                Paragraph(_text(prediction), styles["VerdictValue"]),
                Spacer(1, 4),
                Paragraph(verdict_summary, styles["VerdictCopy"]),
            ],
            [
                Paragraph("RISK LEVEL", styles["VerdictLabel"]),
                Spacer(1, 5),
                Paragraph(_text(risk), styles["VerdictValue"]),
                Spacer(1, 4),
                Paragraph("Use this result as a signal, not proof of payment.", styles["VerdictCopy"]),
            ],
        ]],
        colWidths=[document.width * .68, document.width * .32],
    )
    verdict.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), verdict_color),
        ("BOX", (0, 0), (-1, -1), 0, verdict_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 15),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LINEBEFORE", (1, 0), (1, 0), .6, colors.HexColor("#6f876f")),
    ]))
    story.extend([verdict, Spacer(1, 11)])

    metrics = Table([[
        [Paragraph("MODEL CONFIDENCE", styles["MetricLabel"]), Spacer(1, 4), Paragraph(_text(confidence), styles["MetricValue"])],
        [Paragraph("TRUST SCORE", styles["MetricLabel"]), Spacer(1, 4), Paragraph(_text(trust), styles["MetricValue"])],
        [Paragraph("RISK ASSESSMENT", styles["MetricLabel"]), Spacer(1, 4), Paragraph(_text(risk), styles["MetricValue"])],
    ]], colWidths=[document.width / 3] * 3)
    metrics.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER),
        ("BOX", (0, 0), (-1, -1), .6, LINE),
        ("INNERGRID", (0, 0), (-1, -1), .6, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story.extend([metrics, Spacer(1, 16)])

    detail_rows = [
        ("Amount", f"INR {_text(amount)}"),
        ("Payment app", _text(payment_app)),
        ("Bank", _text(bank)),
        ("Sender", _text(sender)),
        ("Receiver", _text(receiver)),
        ("UPI ID", _text(upi)),
        ("UPI transaction ID", _text(txn)),
        ("Google transaction ID", _text(google_txn)),
        ("Date & time", " · ".join(filter(None, [str(date or ""), str(time or "")])) or "Not available"),
    ]
    detail_table = Table(
        [[Paragraph(_text(label), styles["TableLabel"]), Paragraph(value, styles["TableValue"])]
         for label, value in detail_rows],
        colWidths=[document.width * .70 * .34, document.width * .70 * .66],
        repeatRows=0,
    )
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), PAPER),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [WHITE, colors.HexColor("#fbfcfa")]),
        ("LINEBELOW", (0, 0), (-1, -1), .45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    image_column = [
        Paragraph("Submitted image", styles["SectionHeading"]),
        Paragraph("Original receipt", styles["SectionSubtitle"]),
        Spacer(1, 9),
    ]
    if image_path and os.path.exists(image_path):
        image_column.append(Image(
            image_path,
            width=document.width * .25,
            height=2.2 * inch,
            kind="bound",
            hAlign="CENTER",
        ))
    else:
        image_column.append(Paragraph("Image unavailable.", styles["SmallCopy"]))

    details_column = [
        Paragraph("Receipt details", styles["SectionHeading"]),
        Paragraph("Information extracted from the submitted image.", styles["SectionSubtitle"]),
        Spacer(1, 9),
        detail_table,
    ]
    details_grid = Table(
        [[details_column, image_column]],
        colWidths=[document.width * .70, document.width * .30],
        hAlign="LEFT",
    )
    details_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 10),
        ("LEFTPADDING", (1, 0), (1, -1), 10),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBEFORE", (1, 0), (1, 0), .6, LINE),
    ]))
    story.extend([details_grid, Spacer(1, 12)])

    story.append(PageBreak())
    story.extend([
        Paragraph("ANALYSIS NOTES", styles["ReportEyebrow"]),
        Paragraph("Signals &amp; context", styles["ReportTitle"]),
        Paragraph("The checks and explanatory notes associated with this assessment.", styles["ReportSubtitle"]),
    ])

    story.extend(_section_heading("Checks performed", "Signals reviewed during receipt analysis.", styles))
    feature_rows = [
        [Paragraph(_text(feature), styles["TableValue"]), Paragraph("REVIEWED", styles["MetricLabel"])]
        for feature in safe_features
    ]
    if not feature_rows:
        feature_rows = [[Paragraph("No feature details were provided.", styles["TableValue"]), ""]]
    feature_column_width = document.width * .60
    feature_table = Table(
        feature_rows,
        colWidths=[feature_column_width * .72, feature_column_width * .28]
    )
    feature_table.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, PAPER]),
        ("LINEBELOW", (0, 0), (-1, -1), .45, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (1, 0), (1, -1), GREEN),
    ]))
    if heatmap_path and os.path.exists(heatmap_path):
        heatmap_panel = [
            Paragraph("Visual analysis", styles["SectionHeading"]),
            Paragraph("Model-generated heatmap.", styles["SectionSubtitle"]),
            Spacer(1, 9),
            Image(
                heatmap_path,
                width=document.width * .36,
                height=1.8 * inch,
                kind="bound",
                hAlign="CENTER",
            ),
        ]
    else:
        heatmap_panel = [
            Paragraph("Visual analysis", styles["SectionHeading"]),
            Paragraph("No heatmap was generated for this review.", styles["SmallCopy"]),
        ]

    signals_grid = Table(
        [[feature_table, heatmap_panel]],
        colWidths=[feature_column_width, document.width * .40],
        hAlign="LEFT",
    )
    signals_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (0, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 12),
        ("LEFTPADDING", (1, 0), (1, -1), 12),
        ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBEFORE", (1, 0), (1, 0), .6, LINE),
    ]))
    story.extend([signals_grid, Spacer(1, 15)])

    story.extend(_section_heading("Model explanation", styles=styles))
    explanation_text = (
        "<br/>".join(_text(line) for line in explanation)
        if isinstance(explanation, (list, tuple))
        else _text(explanation)
    )
    explanation_table = Table(
        [[Paragraph(explanation_text, styles["BodyCopy"])]],
        colWidths=[document.width],
    )
    explanation_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PAPER),
        ("BOX", (0, 0), (-1, -1), .6, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    story.extend([explanation_table, Spacer(1, 16)])

    if safe_scores:
        story.extend(_section_heading("Decision breakdown", "Model-provided signal scores.", styles))
        score_rows = [
            [Paragraph(_text(key), styles["TableValue"]), Paragraph(f"{_text(value)}%", styles["TableValue"])]
            for key, value in safe_scores.items()
        ]
        score_table = Table(score_rows, colWidths=[document.width * .78, document.width * .22])
        score_table.setStyle(TableStyle([
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, PAPER]),
            ("LINEBELOW", (0, 0), (-1, -1), .45, LINE),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.extend([score_table, Spacer(1, 16)])

    if safe_reasons:
        story.extend(_section_heading("Additional signals", styles=styles))
        for reason in safe_reasons:
            story.extend([
                Paragraph(f"<font color='#337c60'>•</font> &nbsp;{_text(reason)}", styles["BodyCopy"]),
                Spacer(1, 5),
            ])

    story.extend([
        Spacer(1, 15),
        Paragraph(
            "<b>Important:</b> This report summarizes an AI-assisted review of an image. "
            "It cannot establish that funds were transferred or guarantee that a receipt is authentic. "
            "Confirm the transaction directly in your bank or payment app.",
            styles["SmallCopy"],
        ),
    ])

    document.build(story, onFirstPage=_page_chrome, onLaterPages=_page_chrome)
    return pdf_path
