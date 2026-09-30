from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def render_recovery_packet_pdf(packet: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("PRIMHORA Evidence Packet", styles["Title"]),
        Paragraph("READ-ONLY CASE MATERIAL", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph(f"Case: {packet.get('case_id', '')}", styles["BodyText"]),
        Paragraph(f"Organization: {packet.get('merchant_name', '')}", styles["BodyText"]),
        Paragraph("PRIMHORA does not execute financial recovery. This packet contains evidence and source-backed analysis for authorized human action.", styles["BodyText"]),
        Spacer(1, 12),
    ]

    rows = [["Payout", "Timestamp", "Beneficiary", "Amount", "Status", "Source"]]
    for item in packet.get("transaction_table", []):
        rows.append([
            str(item.get("payout_id", "")),
            str(item.get("timestamp", "")),
            str(item.get("beneficiary", "")),
            str(item.get("amount", "")),
            str(item.get("status", "")),
            str(item.get("source_reference", "")),
        ])
    if len(rows) > 1:
        table = Table(rows, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eeeeee")),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTSIZE", (0,0), (-1,-1), 7),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.extend([Paragraph("Financial chronology", styles["Heading2"]), table, Spacer(1, 12)])

    story.append(Paragraph("Outstanding questions", styles["Heading2"]))
    for question in packet.get("outstanding_questions", []):
        story.append(Paragraph(f"• {question}", styles["BodyText"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Evidence index", styles["Heading2"]))
    for evidence in packet.get("evidence_index", []):
        story.append(Paragraph(
            f"{evidence.get('filename', '')} | SHA-256 {evidence.get('sha256', '')} | {evidence.get('extraction_status', '')}",
            styles["BodyText"],
        ))

    doc.build(story)
    return buffer.getvalue()
