"""
pdf_builder.py
Generates a formal legal complaint PDF in English.
Fills a structured template with the incident details and legal match.
No LLM — deterministic templating for legal reliability.
"""
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Output directory for generated PDFs
_OUTPUT_DIR = Path(__file__).parent.parent / "generated_pdfs"
_OUTPUT_DIR.mkdir(exist_ok=True)


def build_pdf(
    incident_type: str,
    district: str,
    law: dict,
    narrative: str,
    authority: str,
    complainant_id: str = "Anonymous Citizen",
    date_override: Optional[str] = None
) -> str:
    """
    Builds a formal legal complaint PDF.

    Args:
        incident_type: e.g. "caste_discrimination"
        district: District name
        law: Legal graph node dict (act, sections, authority, etc.)
        narrative: Agent-generated formal narrative
        authority: Recipient authority
        complainant_id: Pseudonym or "Anonymous Citizen"
        date_override: Optional date string override

    Returns:
        File path to generated PDF (relative, for serving)
    """
    if not REPORTLAB_AVAILABLE:
        # Fallback: write a .txt complaint if reportlab not installed
        return _build_txt_fallback(incident_type, district, law, narrative, authority, complainant_id)

    date_str = date_override or datetime.now().strftime("%d %B %Y")
    filename = f"complaint_{incident_type}_{district}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = _OUTPUT_DIR / filename

    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Header ────────────────────────────────────────────────────────────────
    story.append(Paragraph("CIVIC-SHIELD", _style(styles, "Title", fontSize=18, spaceAfter=4)))
    story.append(Paragraph("Legal Grievance Complaint", _style(styles, "Heading1", fontSize=14, spaceAfter=2)))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 0.3 * cm))

    # ── Metadata Table ────────────────────────────────────────────────────────
    meta_data = [
        ["Date", date_str],
        ["Complainant", complainant_id],
        ["District", district],
        ["Incident Type", incident_type.replace("_", " ").title()],
        ["To", authority or law.get("authority", "District Collector")],
    ]
    meta_table = Table(meta_data, colWidths=[4 * cm, 13 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f0f4ff"), colors.white]),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Subject Line ──────────────────────────────────────────────────────────
    subject = f"Subject: Complaint regarding {incident_type.replace('_', ' ').title()} — {law.get('act', '')}"
    story.append(Paragraph(subject, _style(styles, "Normal", fontSize=11, bold=True, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.3 * cm))

    # ── Salutation ────────────────────────────────────────────────────────────
    story.append(Paragraph(f"Respected {authority or 'Sir/Madam'},", _style(styles, "Normal", fontSize=11, spaceAfter=8)))

    # ── Narrative ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Statement of Facts", _style(styles, "Heading2", fontSize=12, spaceAfter=4)))
    story.append(Paragraph(narrative or "Details of the incident as narrated by the complainant.", _style(styles, "Normal", fontSize=10.5, spaceAfter=12)))

    # ── Legal Provisions ──────────────────────────────────────────────────────
    story.append(Paragraph("Applicable Legal Provisions", _style(styles, "Heading2", fontSize=12, spaceAfter=4)))
    legal_rows = [
        ["Act / Scheme", law.get("act", "N/A")],
        ["Sections", ", ".join(law.get("sections", []))],
        ["Relief Available", "\n".join(law.get("relief_types", []))],
        ["Helpline", law.get("helpline", "1916")],
        ["Timeline", f"{law.get('timeline_days', 30)} days for response"],
    ]
    legal_table = Table(legal_rows, colWidths=[4.5 * cm, 12.5 * cm])
    legal_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#fff8e7"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))
    story.append(legal_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Prayer ────────────────────────────────────────────────────────────────
    story.append(Paragraph("Prayer / Relief Sought", _style(styles, "Heading2", fontSize=12, spaceAfter=4)))
    relief = law.get("relief_types", ["Appropriate legal relief"])
    for r in relief:
        story.append(Paragraph(f"• {r}", _style(styles, "Normal", fontSize=10.5)))
    story.append(Spacer(1, 0.3 * cm))

    # ── Escalation Path ───────────────────────────────────────────────────────
    if law.get("escalation_path"):
        story.append(Paragraph("Escalation Path", _style(styles, "Heading2", fontSize=12, spaceAfter=4)))
        path = " → ".join(law["escalation_path"])
        story.append(Paragraph(path, _style(styles, "Normal", fontSize=10)))
        story.append(Spacer(1, 0.3 * cm))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        f"This complaint has been auto-generated by CIVIC-SHIELD on {date_str}. "
        "Complainant identity is protected under end-to-end anonymization.",
        _style(styles, "Normal", fontSize=8, color=colors.grey)
    ))

    doc.build(story)
    return str(filepath)


def _style(styles, name, fontSize=10, bold=False, spaceAfter=6, color=None):
    """Helper to create a custom ParagraphStyle."""
    from reportlab.lib.styles import ParagraphStyle as PS
    base = styles[name] if name in styles else styles["Normal"]
    return PS(
        name + str(fontSize),
        parent=base,
        fontSize=fontSize,
        fontName="Helvetica-Bold" if bold else "Helvetica",
        spaceAfter=spaceAfter,
        textColor=color or colors.black
    )


def _build_txt_fallback(incident_type, district, law, narrative, authority, complainant_id) -> str:
    """Fallback plain-text complaint when ReportLab is not installed."""
    date_str = datetime.now().strftime("%d %B %Y")
    filename = f"complaint_{incident_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = _OUTPUT_DIR / filename

    content = f"""CIVIC-SHIELD — LEGAL COMPLAINT
{'='*60}
Date: {date_str}
Complainant: {complainant_id}
District: {district}
To: {authority}

INCIDENT: {incident_type.replace('_', ' ').title()}

APPLICABLE LAW: {law.get('act', 'N/A')}
SECTIONS: {', '.join(law.get('sections', []))}

STATEMENT OF FACTS:
{narrative}

RELIEF SOUGHT:
{chr(10).join('• ' + r for r in law.get('relief_types', []))}

Helpline: {law.get('helpline', '1916')}
{'='*60}
Auto-generated by CIVIC-SHIELD. Identity protected.
"""
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)
