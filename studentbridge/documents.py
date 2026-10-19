"""Branded English PDF documents from validated application facts.

Planning invoices are estimates, not university-issued bills. Transfer receipts
state the simulated status prominently. We never accept an arbitrary JSON dump
as invoice content or change the ledger while generating a PDF.
"""

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
import hashlib
import json
import threading

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
RED = colors.HexColor("#a12d3a")
GOLD = colors.HexColor("#c89c46")
INK = colors.HexColor("#233044")
MUTED = colors.HexColor("#596478")
LINE = colors.HexColor("#e4ded4")
FOOTER = "Invoice is Computer Generated, NO need signature"
FONT_LOCK = threading.Lock()


def _register_fonts():
    with FONT_LOCK:
        if "SB" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("SB", str(ROOT / "assets/fonts/DejaVuSans.ttf")))
            pdfmetrics.registerFont(
                TTFont("SB-Bold", str(ROOT / "assets/fonts/DejaVuSans-Bold.ttf"))
            )
            pdfmetrics.registerFontFamily(
                "SB", normal="SB", bold="SB-Bold", italic="SB", boldItalic="SB-Bold"
            )


def _text(value):
    return escape(str(value)).replace("\n", "<br/>")


def _time(value):
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, timezone.utc).strftime("%d %b %Y, %H:%M UTC")
    return str(value or "Not specified")


def _document_id(kind, payload):
    if kind == "receipt":
        # Replaying a completed transfer must not create a new receipt identity.
        return "SB-RCP-" + str(payload["quote_id"]).upper()
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode()
    return f"SB-{kind.upper()}-{hashlib.sha256(raw).hexdigest()[:12].upper()}"


def _pdf(title, kind, payload, sections, *, banner=None, notes=()):
    _register_fonts()
    output = BytesIO()
    body = ParagraphStyle(
        "SBBody",
        fontName="SB",
        fontSize=9,
        leading=14,
        textColor=INK,
        spaceAfter=5,
        splitLongWords=True,
    )
    heading = ParagraphStyle(
        "SBHeading",
        parent=body,
        fontName="SB-Bold",
        fontSize=11,
        spaceBefore=17,
        spaceAfter=8,
        textColor=RED,
        keepWithNext=True,
    )
    label = ParagraphStyle("SBLabel", parent=body, fontSize=8.5, textColor=MUTED)
    value = ParagraphStyle("SBValue", parent=body, fontName="SB-Bold", fontSize=9)
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=43,
        leftMargin=43,
        topMargin=137,
        bottomMargin=64,
        title=f"StudentBridge - {title}",
        author="StudentBridge",
        subject="Student finance document",
    )
    document_id = _document_id(kind, payload)
    issued = _time(
        payload.get("issued_at")
        or payload.get("executed_at")
        or payload.get("created_at")
        or datetime.now(timezone.utc).timestamp()
    )

    def frame(canvas, active_doc):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(RED)
        canvas.rect(0, height - 12, width, 12, stroke=0, fill=1)
        canvas.setFillColor(GOLD)
        canvas.rect(width - 118, height - 12, 118, 12, stroke=0, fill=1)
        canvas.setFont("SB-Bold", 25)
        canvas.setFillColor(RED)
        canvas.drawString(43, height - 57, "StudentBridge")
        canvas.setFont("SB", 9)
        canvas.setFillColor(MUTED)
        canvas.drawString(44, height - 77, title)
        canvas.setFont("SB", 7.8)
        canvas.drawRightString(width - 43, height - 51, document_id)
        canvas.drawRightString(width - 43, height - 68, issued)
        canvas.setStrokeColor(LINE)
        canvas.line(43, height - 102, width - 43, height - 102)
        canvas.line(43, 51, width - 43, 51)
        canvas.setFont("SB", 8)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(width / 2, 33, FOOTER)
        canvas.setFont("SB", 7)
        canvas.drawRightString(width - 43, 20, f"Page {active_doc.page}")
        canvas.restoreState()

    story = []
    if banner:
        box = Table(
            [
                [
                    Paragraph(
                        _text(banner),
                        ParagraphStyle(
                            "SBBanner",
                            parent=body,
                            fontName="SB-Bold",
                            textColor=RED,
                            fontSize=9,
                            spaceAfter=0,
                        ),
                    )
                ]
            ],
            colWidths=[509],
        )
        box.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff2e6")),
                    ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
                    ("TOPPADDING", (0, 0), (-1, -1), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
                    ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ]
            )
        )
        story.extend([box, Spacer(1, 5)])
    for section_title, rows in sections:
        story.append(Paragraph(_text(section_title), heading))
        data = [[Paragraph(_text(k), label), Paragraph(_text(v), value)] for k, v in rows]
        if not data:
            data = [[Paragraph("No activity recorded.", body), Paragraph("-", body)]]
        table = Table(data, colWidths=[181, 328], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.35, LINE),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    (
                        "ROWBACKGROUNDS",
                        (0, 0),
                        (-1, -1),
                        [colors.white, colors.HexColor("#faf8f4")],
                    ),
                ]
            )
        )
        # Rows split between pages, while each financial label/value row stays together.
        story.append(table)
    if notes:
        story.append(Paragraph("Document notes", heading))
        for note in notes:
            story.append(Paragraph(_text(note), body))
    doc.build(story, onFirstPage=frame, onLaterPages=frame)
    return output.getvalue()


def transfer_receipt(receipt):
    sections = [
        (
            "Receipt details",
            [
                ("Receipt reference", receipt["quote_id"]),
                ("Status", "Completed simulation - no real money moved"),
                ("Simulation provider", receipt["provider"]),
                ("Processed at", _time(receipt["executed_at"])),
                (
                    "Original receipt returned",
                    "Yes - no second debit" if receipt.get("replayed") else "No",
                ),
            ],
        ),
        (
            "Transfer amounts",
            [
                ("Total spend", f"{receipt['spent']} {receipt['source']}"),
                ("Fee included in spend", f"{receipt['fee_included']} {receipt['source']}"),
                ("Amount received", f"{receipt['received']} {receipt['target']}"),
                (
                    "Reference data",
                    "Published rates" if receipt["fx_mode"] == "live" else "Illustrative rates",
                ),
            ],
        ),
    ]
    return _pdf(
        "Transfer Receipt",
        "receipt",
        receipt,
        sections,
        banner="SIMULATED TRANSACTION - NO REAL MONEY MOVED",
        notes=[
            "This receipt records a StudentBridge wallet simulation. It is not bank payment confirmation.",
            "The fee is included in the total spend, not charged again.",
        ],
    )


def planning_invoice(bundle, record):
    result, inputs = bundle["result"], bundle["inputs"]
    code = result["currency"]
    rows = [
        ("University", record["university"]),
        ("Programme", record["programme"]),
        ("Location", f"{record['city']}, {record['country']}"),
        ("Student classification", record["student_type"]),
        ("Planning horizon", f"{result['months']} months"),
        ("Fee period / count", f"{result['fee_period']} / {result['tuition_periods']}"),
        ("Fee per period (entered)", f"{inputs['tuition']} {code}"),
    ]
    amounts = [
        ("Tuition", result["tuition"]),
        ("Tax assumption", result["tax_assumption"]),
        ("Living costs", result["living_total"]),
        ("One-off charges", result["one_off"]),
        ("Contingency", result["contingency"]),
        ("TOTAL ESTIMATED COST", result["total"]),
        ("Confirmed resources", result["resources"]),
        ("FUNDING GAP", result["funding_gap"]),
    ]
    monthly = [(f"Monthly {key}", f"{value} {code}") for key, value in inputs["living"].items()]
    return _pdf(
        "Planning Invoice",
        "invoice",
        bundle,
        [
            ("Invoice details", rows),
            ("Estimated charges and funding", [(k, f"{v} {code}") for k, v in amounts]),
            ("Monthly living assumptions", monthly),
        ],
        banner="UNPAID PLANNING ESTIMATE - NOT A UNIVERSITY-ISSUED BILL",
        notes=[
            "No payment is requested or confirmed by this document.",
            "Amounts are based on your entered fee, period, living costs, tax and contingency assumptions.",
            "University fee reference: " + record["source_url"],
            "Source checked: "
            + record["checked_on"]
            + ". Confirm the current applicable invoice with the university.",
        ],
    )


def conversion_statement(result):
    ref = result["reference"]
    return _pdf(
        "Currency Conversion Statement",
        "fx",
        result,
        [
            (
                "Conversion details",
                [
                    ("Source amount", f"{result['amount']} {result['base']}"),
                    ("Converted reference amount", f"{result['converted']} {result['target']}"),
                    ("Reference rate", ref["rate"]),
                    ("Observation date", ref["as_of"]),
                    (
                        "Rate source",
                        ref["source"]
                        if ref["mode"] == "live"
                        else "Illustrative reference dataset",
                    ),
                ],
            )
        ],
        banner="REFERENCE CALCULATION - NOT A PAYMENT CONFIRMATION",
        notes=[
            "Bank and licensed remittance provider rates and fees may differ.",
            "RMB denotes CNY. CNH, when available, is a separate offshore reference.",
        ],
    )


def university_statement(record):
    fee = (
        f"{record['fee']} {record['currency']} / {record['fee_period']}"
        if record["fee"] is not None
        else "Requires a current fee sheet"
    )
    return _pdf(
        "University Fee Reference",
        "university",
        record,
        [
            (
                "Programme reference",
                [
                    ("University", record["university"]),
                    ("Programme", record["programme"]),
                    ("Location", f"{record['city']}, {record['country']}"),
                    ("Student classification", record["student_type"]),
                    ("Published fee", fee),
                    ("Source year", record["source_year"]),
                    ("Checked on", record["checked_on"]),
                ],
            )
        ],
        banner="PUBLISHED REFERENCE - NOT AN INVOICE OR ADMISSION OFFER",
        notes=[record["notes"], "Official source: " + record["source_url"]],
    )


def audit_statement(audit):
    integrity = audit["global_integrity"]
    events = [
        (
            f"#{row['seq']} - {_time(row['stamp'])}",
            row["event"].replace("sandbox_", "simulation_").replace("_", " "),
        )
        for row in audit["own_events"]
    ]
    return _pdf(
        "Activity and Audit Statement",
        "audit",
        audit,
        [
            (
                "Audit verification",
                [
                    ("Local chain integrity", "Verified" if integrity["valid"] else "Failed"),
                    ("Verified event count (export scope)", integrity["rows"]),
                    ("Audit head", integrity.get("head", "Unavailable")),
                ],
            ),
            ("Your activity", events),
        ],
        notes=[
            "Events represent StudentBridge account activity and simulated financial operations.",
            "Keep the audit head outside the runtime directory to support later rollback checks.",
        ],
    )


def comparison_statement(options):
    first = options[0]
    from .money import major

    rows = []
    for option in options:
        rows.append(
            (
                option["provider"],
                f"Spend {major(option['spend_minor'], option['source'])} {option['source']}; "
                f"fee included {major(option['fee_minor'], option['source'])}; "
                f"receive {major(option['receive_minor'], option['target'])} {option['target']}",
            )
        )
    return _pdf(
        "Transfer Options Statement",
        "options",
        {"options": options},
        [("Provider comparison", rows)],
        banner="SIMULATED PROVIDERS - NOT EXECUTABLE BANK QUOTES",
        notes=[
            "Reference observation date: " + first["reference"]["as_of"],
            "Create a new signed quote and review it before confirming a simulation.",
        ],
    )


def student_profile_pdf(profile):
    def money(item):
        return f"{item['amount']} {item['currency']}"

    return _pdf(
        "Student Profile Summary",
        "profile",
        profile,
        [
            (
                "Study details",
                [
                    ("University", profile["university"]),
                    ("Department / faculty", profile["department"]),
                    ("Programme", profile["programme"]),
                    ("Campus", profile["campus"] or "Not specified"),
                    ("Study location", f"{profile['city']}, {profile['country']}"),
                    ("Study mode", profile["study_mode"]),
                ],
            ),
            (
                "User-confirmed planning inputs",
                [
                    ("Planning start", profile["start_date"]),
                    ("Horizon", f"{profile['months']} months"),
                    ("Tuition", money(profile["tuition"]) + " / " + profile["fee_period"]),
                    ("Next unpaid tuition date", profile["next_tuition_date"]),
                    (
                        "Billing interval",
                        f"{profile['billing_interval_months']} months; zero means once",
                    ),
                    *[(f"Monthly {k}", money(v)) for k, v in profile["living"].items()],
                    ("Savings", money(profile["savings"])),
                    ("Monthly confirmed income", money(profile["monthly_income"])),
                    ("Confirmed funding", money(profile["confirmed_funding"])),
                    ("One-time expenses", money(profile["one_off"])),
                ],
            ),
        ],
        banner="USER-PROVIDED INPUTS - NOT AN OFFICIAL UNIVERSITY DOCUMENT",
        notes=[
            "Updated: " + profile.get("updated_at", "Not specified"),
            "Amounts were confirmed by the user and are not independently verified.",
            "Private notes are omitted from this summary. Downloaded documents contain personal financial information.",
        ],
    )


def forecast_pdf(profile, result):
    code = result["currency"]
    refs = [
        (
            f"{r['base']} to {r['quote']}",
            f"Rate {r['rate']}; observed {r['as_of']}; fetched {r['fetched_at']}; {r['source']}",
        )
        for r in result["references"]
    ]
    return _pdf(
        "Personal Budget Forecast",
        "forecast",
        result,
        [
            (
                "Forecast details",
                [
                    ("University", profile["university"]),
                    ("Programme", profile["programme"]),
                    ("Profile updated", profile.get("updated_at", "Not specified")),
                    ("Planning starts", profile["start_date"]),
                    ("Horizon", f"{result['months']} months"),
                    ("Estimated cost", f"{result['total']} {code}"),
                    ("Declared resources", f"{result['resources']} {code}"),
                    ("Overall funding gap", f"{result['funding_gap']} {code}"),
                    ("Largest monthly cash shortfall", f"{result['upfront_timing_gap']} {code}"),
                ],
            ),
            (
                "Scenario assumptions",
                [
                    (
                        "Living-cost growth",
                        profile["annual_cost_growth_percent"] + "% nominal annual",
                    ),
                    ("Foreign expense stress", profile["fx_stress_percent"] + "%"),
                    ("Reserve buffer", profile["buffer_percent"] + "%"),
                ],
            ),
            (
                "Monthly cash flow",
                [
                    (
                        row["month"],
                        f"Cost {row['cost']} {code}; income {row['income']}; closing balance {row['closing_balance']}; tuition dates: {row['tuition_due_dates'] or 'none'}",
                    )
                    for row in result["rows"]
                ],
            ),
            (
                "Exchange-rate references",
                refs or [("Currency", "All inputs use the report currency; no rate needed")],
            ),
        ],
        banner="PLANNING ESTIMATE - FUTURE FEES AND EXCHANGE RATES ARE UNKNOWN",
        notes=result["assumptions"] + [result["source"]],
    )
